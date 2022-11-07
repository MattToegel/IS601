import pytest


@pytest.fixture()
def app():
    from ..main import create_app
    from ..sql.db import DB
    app = create_app()
    """app.config.update({
        "TESTING": True,
    })"""

    # other setup can go here
    yield app
    DB.close()
    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

# Note: this test will insert/update new company/employee data and won't clean it up
def test_upload_csv(client):
    import os
    CURR_DIR = os.path.dirname(os.path.abspath(__file__))
    file = f"{CURR_DIR}/test-csv.csv"
    data = {
        "file": (open(file, 'rb'), file)
    }
    resp = client.post("/admin/import", data=data)
    assert resp.status_code == 200
    import io
    import csv
    stream = io.TextIOWrapper(open(file, 'rb'), "UTF8", newline=None)
    companies = []
    employees = []
    for row in csv.DictReader(stream, delimiter=','):
        if row["company_name"] and row["address"] and row["city"] and row["state"] and row["zip"] and row["web"]:
            companies.append(row["company_name"])
            
        if row["first_name"] and row["last_name"] and row["email"] and row["company_name"]:
            employees.append(row["first_name"] + row["last_name"])
    company_count = len(companies)
    employee_count = len(employees)
    from ..sql.db import DB
    format_strings = ','.join(['%s'] * company_count)
    result = DB.selectOne("SELECT count(1) as c FROM IS601_MP2_Companies WHERE name in (%s)" % format_strings, *tuple(companies))
    print(result.row)
    assert result.row["c"] == company_count
    format_strings = ','.join(['%s'] * employee_count)
    result = DB.selectOne("SELECT count(1) as e FROM IS601_MP2_Employees WHERE CONCAT_WS('',first_name, last_name) in (%s)" % format_strings, *tuple(employees))
    print(result.row)
    assert result.row["e"] == employee_count