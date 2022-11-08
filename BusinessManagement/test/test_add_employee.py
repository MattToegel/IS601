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
    try:
        DB.getDB().autocommit = True
        DB.delete("DELETE FROM IS601_MP2_Employees WHERE first_name = %s and last_name=%s", "delme","delme")
        # reset AUTO_INCREMENT value to max id + 1 so test cases don't cause large id gaps

        # this needs to run at the end of the other tests
        # if this hangs (takes longer than 10 seconds) run the following commands manually via your mysql extension
        # show processlist;
        # kill #;
        # the # will be the process id of the sleeping query
        result = DB.query(""" set session wait_timeout = 1;
        ALTER TABLE IS601_MP2_Employees AUTO_INCREMENT = 1;
        """)
        print("result", result.status)
    except Exception as e:
        print(e)
    DB.close()
    # clean up / reset resources here

@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

#https://pypi.org/project/pytest-order/
@pytest.mark.order("last")
def test_add_employee(client):
    from ..sql.db import DB
    resp = client.post("/employee/add", data={
        "first name": "delme",
        "last name": "delme",
        "email": "delme@delme.com"
    }, follow_redirects=True )
    assert resp.status_code == 200
    result = DB.selectOne("SELECT id from IS601_MP2_Employees where first_name = %s and last_name = %s LIMIT 1", 'delme', 'delme')
    if result and result.row:
        id = int(result.row["id"])
        print("id", id)
        resp = client.get(f"/employee/edit?id={id}", follow_redirects=True )
        # print(resp.data)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.data, "html.parser")
        form = soup.form
        ele = form.select("[name='last_name']")[0]
        print(ele)
        assert ele.get("value") == 'delme'
        ele = form.select("[name='first_name']")[0]
        assert ele.get("value") == 'delme'