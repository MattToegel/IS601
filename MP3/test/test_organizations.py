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
    DB.delete("DELETE FROM IS601_MP3_Organizations WHERE name in (%s, %s, %s,%s)", "tctest_delme1","tctest_delme2","tctest_delme3","tctest_delme4")
    yield app
    print("cleaning up")
    DB.getDB().autocommit = True
    DB.delete("DELETE FROM IS601_MP3_Organizations WHERE name in (%s, %s, %s, %s)", "tctest_delme1","tctest_delme2","tctest_delme3","tctest_delme4")
   
    # this needs to run at the end of the other tests
    # if this hangs (takes longer than 10 seconds) run the following commands manually via your mysql extension
    # show processlist;
    # kill #;
    # the # will be the process id of the sleeping query
    # reset AUTO_INCREMENT value to max id + 1 so test cases don't cause large id gaps
    result = DB.query("""ALTER TABLE IS601_MP3_Organizations AUTO_INCREMENT = 1;
    """)
    # clean up / reset resources here


@pytest.fixture(scope='module')
def client(app):
    return app.test_client()


fake_id_2 = 0
@pytest.fixture(scope='module')
def fake_org_2(client):
    DB.getDB().autocommit = True
    result = DB.insertOne("""INSERT INTO IS601_MP3_Organizations (
                 name,
                 address,
                 city,
                 country,
                 state,
                 zip,
                 website,
                 description
                 )
                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""", 
                 *("tctest_delme2", "fake", "fake", "US", "NJ", "07072","www.example.com","fake"))
    assert result.insert_id > 0, "failed to insert record"
    resp = client.get(f"/organization/edit?id={result.insert_id}")
    global fake_id_2
    fake_id_2 = result.insert_id
    soup = BeautifulSoup(resp.data, "html.parser")

    return soup
    
def test_organization_form(fake_org_2):
    test_list = ["name", "address", "city", "state", "country", "website", "zip","description"]
    form = fake_org_2
    assert form, "Failed to load form"
    for i in test_list:
        ele = form.select_one(f"[name={i}]")
        label = form.select_one(f"[for={i}]")
        assert ele, f"Missing element for {i}"
        assert ele.get("id"), f"Input element {i} is missing id"
        assert label, f"Input element {i} is missing label or proper 'for' attribute"

def test_organization_edit(fake_org_2, client):
    test_dict = {
        "name":"tctest_delme2",
        "address":"fake2",
        "city":"fake2",
        "country": "US",
        "state":"NY",
        "zip": "07060",
        "website": "http://www.example2.com",
        "description": "fake2"
    }
   
    resp = client.post(f"/organization/edit?id={fake_id_2}", data=test_dict, follow_redirects=True)
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
    
    
def test_organization_add(client):
    test_dict = {
        "name":"tctest_delme3",
        "address":"fake3",
        "city":"fake3",
        "country": "US",
        "state":"NY",
        "zip": "07060",
        "website": "http://www.example3.com",
        "description": "fake3"
    }
    resp = client.post("/organization/add", data=test_dict, follow_redirects=True)
    assert resp.status_code == 200, "Non-success response code from server"
    #import time
    #time.sleep(.1)
    result = DB.selectOne("SELECT * from IS601_MP3_Organizations WHERE name = %(name)s", {"name":"tctest_delme3"})
    if result and result.row:
        for k,v in test_dict.items():
            check = result.row.get(k)
            assert str(check) == str(v), f"{k} didn't save or wasn't properly assigned"
    else:
        assert False, "Test donation didn't persist to database"

def test_organization_delete(client):
    result = DB.insertOne("""INSERT INTO IS601_MP3_Organizations (
                 name,
                 address,
                 city,
                 country,
                 state,
                 zip,
                 website,
                 description
                 )
                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""", 
                 *("tctest_delme4", "fake4", "fake4", "US", "NJ", "07072","www.example4.com","fake4"))
    assert result.insert_id > 0, "failed to insert record"
    id = result.insert_id
    resp = client.get(f"/organization/delete?id={id}", follow_redirects=True)
    assert resp.status_code == 200, "Delete route had unsuccessful status code"
    result = DB.selectOne("SELECT count(1) as count FROM IS601_MP3_Organizations WHERE id = %s", id)
    assert result and result.row, "error checking if db record was deleted"
    assert result.row.get("count") == 0, "failed to delete record"

@pytest.mark.parametrize(
    "allowed_column", 
    ["name", "city", "country", "state", "modified", "created"]
)
def test_organization_list(allowed_column, fake_org_2,client):
    cols = ["name",
                 "address",
                 "city",
                 "country",
                 "state",
                 "zip", "website","donations", "actions"]
    col_names = map(lambda x: x.replace("_"," "), cols)
    cols.remove("actions")
    cols.remove("donations")
    ac = allowed_column
    print(f"Checking list sort on column {ac}")
    resp = client.get(f"/organization/search?limit=3&column={ac}&order=asc")
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
    result = DB.selectAll(f"SELECT {','.join(cols)},(select count(1) FROM IS601_MP3_Donations where organization_id = id) as donations FROM IS601_MP3_Organizations WHERE 1=1 ORDER BY {ac} asc LIMIT 3")
    assert result and result.rows and len(result.rows) > 0, "Organization lookup failed"
    vals = result.rows[0].items()
    #print(tbody_values)
    #print(result.row)
    for k,v in vals:
        i = thead_names.index(k.replace("_"," ").lower())
        assert str(v if v is not None else "none").lower() in tr_values[i], f"Expected value {v} in table cell in column [{i}] {tr_values[i]}"
    
def test_organization_search_form(client):
    resp = client.get("/organization/search")
    soup = BeautifulSoup(resp.data, "html.parser")
    form = soup.form
    assert form, "search form is missing"
    assert form.find(attrs={'name': 'name'}), "Missing organization 'name' field"
    assert form.find(attrs={'name': 'country'}), "Missing country field"
    assert form.find(attrs={'name': 'state'}), "Missing state field"
    assert form.find(attrs={'name': 'column'}), "Missing sort 'col' field"
    assert form.find(attrs={'name': 'order'}), "Missing sort 'order' field"
    assert form.find(attrs={'name': 'limit'}), "Missing limit field"