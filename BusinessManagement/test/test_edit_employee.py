import pytest


@pytest.fixture()
def app():
    from ..main import create_app
    from ..sql.db import DB
    app = create_app()
    """app.config.update({
        "TESTING": True,
    })"""
    DB.getDB().autocommit = True
    # other setup can go here
    DB.delete("DELETE FROM IS601_MP2_Employees WHERE id = %s", -1)
    DB.delete("DELETE FROM IS601_MP2_Companies WHERE id = %s", -1)
    
    DB.insertOne("INSERT INTO IS601_MP2_Companies (id, name) VALUES (-1, '_test-company')")
    DB.insertOne("INSERT INTO IS601_MP2_Employees (id, first_name, last_name, email, company_id) VALUES (-1,'_test', '_test', '_test@email.com', -1)")
    yield app
    DB.delete("DELETE FROM IS601_MP2_Employees WHERE id = %s", -1)
    DB.delete("DELETE FROM IS601_MP2_Companies WHERE id = %s", -1)
    DB.close()
    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

#https://pypi.org/project/pytest-order/
@pytest.mark.order("second_to_last")
def test_edit_employee(client):
    resp = client.post("/employee/edit?id=-1", data={
        "last name": "_test2",
        "company": -1
    }, follow_redirects=True )
    assert resp.status_code == 200
    resp = client.get("/employee/edit?id=-1", follow_redirects=True )
    # print(resp.data)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(resp.data, "html.parser")
    form = soup.form
    ele = form.select("[name='last_name']")[0]
    print(ele)
    assert ele.get("value") == '_test2'
    ele = form.select("[name='company']")[0]
    assert int(ele.get("value")) == -1 

