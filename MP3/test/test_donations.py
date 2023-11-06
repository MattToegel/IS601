import pytest
from bs4 import BeautifulSoup
import datetime
from ..sql.db import DB
@pytest.fixture(scope='module')
def app():
    from ..main import create_app
    
    app = create_app()
    """app.config.update({
        "TESTING": True,
    })"""

    # other setup can go here

    yield app
    print("cleaning up")
    DB.getDB().autocommit = True
    DB.delete("DELETE FROM IS601_MP3_Donations WHERE donor_email in (%s, %s, %s)", "delme1@delme.com","delme2@delme.com","delme3@delme.com")
   
    # this needs to run at the end of the other tests
    # if this hangs (takes longer than 10 seconds) run the following commands manually via your mysql extension
    # show processlist;
    # kill #;
    # the # will be the process id of the sleeping query
    # reset AUTO_INCREMENT value to max id + 1 so test cases don't cause large id gaps
    result = DB.query("""ALTER TABLE IS601_MP3_Donations AUTO_INCREMENT = 1;
    """)
    # clean up / reset resources here


@pytest.fixture(scope='module')
def client(app):
    return app.test_client()


@pytest.fixture(scope="module")
def rand_org():
    result = DB.selectOne("SELECT id FROM IS601_MP3_Organizations LIMIT 1")
    id = None
    if result and result.row:
        id = result.row.get("id")
    assert id > 0, "Invalid organization id"
    return id

fake_id_2 = 0
@pytest.fixture(scope='module')
def fake_donation_2(client, rand_org):
    DB.getDB().autocommit = True
    result = DB.insertOne("""INSERT INTO IS601_MP3_Donations (
                 donor_firstname,
                 donor_lastname,
                 donor_email,
                 organization_id,
                 item_name,
                 item_quantity,
                 donation_date
                 )
                 VALUES (%(fn)s,%(ln)s,%(e)s,%(o)s,%(it)s,%(iq)s,%(dd)s)""", {"fn":'delme2',
                 "ln":'delme2',
                 "e":'delme2@delme.com',
                 "o":f"{rand_org}",
                 "it":'test cheese',
                 "iq":'5',
                 "dd":'2023-10-31'})
    assert result.insert_id > 0, "failed to insert record"
    resp = client.get(f"/donations/edit?id={result.insert_id}")
    global fake_id_2
    fake_id_2 = result.insert_id
    soup = BeautifulSoup(resp.data, "html.parser")

    return soup
    
def test_donation_form(fake_donation_2):
    test_list = ["donor_firstname", "donor_lastname", "donor_email", "organization_id", "item_name", "item_quantity", "item_description","donation_date"]
    form = fake_donation_2
    assert form, "Failed to load form"
    for i in test_list:
        ele = form.select_one(f"[name={i}]")
        label = form.select_one(f"[for={i}]")
        assert ele.get("id"), f"Input element {i} is missing id"
        assert label, f"Input element {i} is missing label or proper 'for' attribute"

def test_donation_edit(fake_donation_2, rand_org, client):
    test_dict = {
        "donor_firstname":"delme3",
        "donor_lastname":"delme3",
        "donor_email":"delme2@delme.com",
        "organization_id": f"{rand_org}",
        "item_name":"test cheese 2",
        "item_quantity": "1",
        "item_description": "",
        "donation_date": "2023-10-30"
    }
    resp = client.post(f"/donations/edit?id={fake_id_2}", data=test_dict, follow_redirects=True)
    soup = BeautifulSoup(resp.data, "html.parser")
    form = soup.form
    assert form, "Form failed to load"
    for k,v in test_dict.items():
        print(f"checking {k} with val {v}")
        ele = form.select_one(f"[name={k}]")
        if ele.name == "input" or ele.name == "select":
            check = ele.get("value")
        else:
            check = ele.text
        assert check == v, f"Failed to populate correct {k}"
    
    
def test_donation_add(client, rand_org):
    id = rand_org
    # Get the current date and time
    now = datetime.datetime.now()
    # Format the date as YYYY-MM-DD
    formatted_date = now.strftime("%Y-%m-%d")
    test_dict ={
        "donor_firstname":"delme1",
        "donor_lastname":"delme1",
        "donor_email":"delme1@delme.com",
        "organization_id": f"{id}",
        "item_name":"cookies",
        "item_quantity": f"10",
        "donation_date": f"{formatted_date}"
    }
    resp = client.post("/donations/add", data=test_dict, follow_redirects=True)
    assert resp.status_code == 200, "Non-success response code from server"
    #import time
    #time.sleep(.1)
    result = DB.selectOne("SELECT * from IS601_MP3_Donations WHERE donor_email = %(email)s", {"email":"delme1@delme.com"})
    if result and result.row:
        for k,v in test_dict.items():
            check = result.row.get(k)
            if k == "donation_date":
                check = check.strftime("%Y-%m-%d")
            assert str(check) == str(v), f"{k} didn't save or wasn't properly assigned"
    else:
        assert False, "Test donation didn't persist to database"

def test_donation_delete(client, rand_org):
    result = DB.insertOne("""INSERT INTO IS601_MP3_Donations (
                 donor_firstname,
                 donor_lastname,
                 donor_email,
                 organization_id,
                 item_name,
                 item_quantity,
                 donation_date
                 )
                 VALUES (%(fn)s,%(ln)s,%(e)s,%(o)s,%(it)s,%(iq)s,%(dd)s)""", {"fn":'delme3',
                 "ln":'delme3',
                 "e":'delme3@delme.com',
                 "o":f"{rand_org}",
                 "it":'test cheese',
                 "iq":'5',
                 "dd":'2023-10-31'})
    assert result.insert_id > 0, "failed to insert record"
    id = result.insert_id
    resp = client.get(f"/donations/delete?id={id}", follow_redirects=True)
    assert resp.status_code == 200, "Delete route had unsuccessful status code"
    result = DB.selectOne("SELECT count(1) as count FROM IS601_MP3_Donations WHERE id = %s", id)
    assert result and result.row, "error checking if db record was deleted"
    assert result.row.get("count") == 0, "failed to delete record"

@pytest.mark.parametrize(
    "allowed_column", 
    ["donor_firstname", "donor_lastname", "donor_email", "organization_name", "item_name", "item_quantity", "created", "modified"]
)
def test_donation_list(allowed_column, fake_donation_2,client):
    cols = ["donor_firstname",
                 "donor_lastname",
                 "donor_email",
                 "item_name",
                 "item_quantity",
                 "donation_date", "comments","organization_name", "actions"]
    col_names = map(lambda x: x.replace("_"," "), cols)
    cols.remove("actions")
    cols.remove("organization_name")
    ac = allowed_column
    print(f"Checking list sort on column {ac}")
    resp = client.get(f"/donations/search?limit=3&column={ac}&order=asc")
    soup = BeautifulSoup(resp.data, "html.parser")
    table = soup.select_one("table")
    
    assert table, "Table wasn't found"
    thead = table.select("th")
    assert thead and len(thead) > 0, "Missing table head"
    #print(thead)
    thead_names = list(map(lambda x:x.text.strip().lower(), thead))
    #print(thead_names)
    for c in col_names:
        assert c in thead_names, f"{c} wasn't found in table head"
    tbody = table.select_one("tbody")
    assert tbody, "Missing table body"
    tr = tbody.select_one("tr").select("td")
    
    tr_values = list(map(lambda x: x.text.strip().lower(), tr))
    c = ac
    if c != "organization_name":
        c = f"D.{c}"
    result = DB.selectAll(f"SELECT {','.join(cols)}, O.name as organization_name FROM IS601_MP3_Donations D LEFT JOIN IS601_MP3_Organizations O on O.id = D.organization_id WHERE 1=1 ORDER BY {c} asc LIMIT 3")
    assert result and result.rows and len(result.rows) > 0, "Donation lookup failed"
    vals = result.rows[0].items()
    #print(tbody_values)
    #print(result.row)
    for k,v in vals:
        i = thead_names.index(k.replace("_"," ").lower())
        assert str(v if v is not None else "none").lower() in tr_values[i], f"Expected value {v} in table cell in column [{i}] {tr_values[i]}"
    
def test_donation_search_form(client):
    resp = client.get("/donations/search")
    soup = BeautifulSoup(resp.data, "html.parser")
    form = soup.form
    assert form, "search form is missing"
    assert form.find(attrs={'name': 'fn'}), "Missing donation 'fn' field"
    assert form.find(attrs={'name': 'ln'}), "Missing donation 'ln' field"
    assert form.find(attrs={'name': 'email'}), "Missing donation 'email' field"
    email_field = form.find(attrs={'name': 'email'})
    print(f"Email field", email_field)
    if email_field:
        print(f"email field type: {email_field.get('type')}")
        assert email_field.get("type") == "text", "Email field should allow partial searching so type 'email' isn't valid"
    assert form.find(attrs={'name': 'organization_id'}), "Missing organization id field"
    assert form.find(attrs={'name': 'column'}), "Missing sort 'col' field"
    assert form.find(attrs={'name': 'order'}), "Missing sort 'order' field"
    assert form.find(attrs={'name': 'limit'}), "Missing limit field"