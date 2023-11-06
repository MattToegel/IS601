import pytest


@pytest.fixture()
def app():
    from ..main import create_app
    from ..sql.db import DB
    app = create_app()
    """app.config.update({
        "TESTING": True,
    })"""
    DB.delete("DELETE FROM IS601_MP3_Donations where donor_email like '%tctest%'")
    DB.delete("DELETE FROM IS601_MP3_Organizations WHERE name like '%tctest'")
    # other setup can go here
    yield app
    DB.delete("DELETE FROM IS601_MP3_Donations where donor_email like '%tctest%'")
    DB.delete("DELETE FROM IS601_MP3_Organizations WHERE name like '%tctest'")
    DB.query("""ALTER TABLE IS601_MP3_Donations AUTO_INCREMENT = 1;""")
    DB.query("""ALTER TABLE IS601_MP3_Organizations AUTO_INCREMENT = 1;""")
    DB.close()
    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


# Note: this test will insert/update new company/employee data and won't clean it up
def test_upload_csv(client):
    import os
    CURR_DIR = os.path.dirname(os.path.abspath(__file__))
    file = f"{CURR_DIR}/test_data.csv"
    data = {
        "file": (open(file, 'rb'), file)
    }
    resp = client.post("/admin/import", data=data)
    assert resp.status_code == 200, "Unsuccessful response code"
    import io
    import csv
    stream = io.TextIOWrapper(open(file, 'rb'), "UTF8", newline=None)
    organizations = []
    donations = []
    for row in csv.DictReader(stream, delimiter=','):
        
        organization_data = {
                    'name': row.get('organization_name'),
                    'address': row.get('organization_address'),
                    'city': row.get('organization_city'),
                    'country': row.get('organization_country'),
                    'state': row.get('organization_state'),
                    'zip': row.get('organization_zip'),
                    'website': row.get('organization_website'),
                    'description': row.get('organization_description')
                }
        name = row.get('donor_name')
        if name and " " in name:
            first = name.split(" ")[0]
            last = name.split(" ")[1]
        donation_data = {
                    'donor_firstname': first,
                    'donor_lastname': last,
                    'donor_email': row.get('donor_email'),
                    'item_name': row.get('item_name'),
                    'item_description': row.get('item_description'),
                    'quantity': row.get('item_quantity'),
                    'organization_name': row.get('organization_name'),
                    'donation_date': row.get('donation_date'),
                    'comments': row.get('comments')
                }
        if  all(organization_data.values()):
            print(organization_data)
            organizations.append(organization_data["name"])
            
        if all(donation_data.values()):
            donations.append(donation_data["donor_email"]+donation_data["item_name"])
    organizations = list(set(organizations))
    donations = list(set(donations))
    org_count = len(organizations)
    donation_count = len(donations)
    from ..sql.db import DB
    format_strings = ','.join(['%s'] * org_count)
    result = DB.selectOne("SELECT count(1) as o FROM IS601_MP3_Organizations WHERE name in (%s)" % format_strings, *tuple(organizations))
    print(result.row)
    assert result.row["o"] == org_count, "Incorrect expected organization insert count"
    format_strings = ','.join(['%s'] * donation_count)
    result = DB.selectOne("SELECT count(1) as d FROM IS601_MP3_Donations WHERE CONCAT_WS('',donor_email, item_name) in (%s)" % format_strings, *tuple(donations))
    print(result.row)
    assert result.row["d"] == donation_count, "Incorrect expected donation insert count"