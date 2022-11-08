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

def get_column_index(target, cells):
    rowIndex = -1
    index = 1
    for th in cells:
        test = th.string.lower().replace(" ", "_")
        if test == target:
            rowIndex = index
            break
        index += 1
    assert rowIndex > 0, f"th for {target} not found"
    return rowIndex
def get_cell_content_by_index(index, table):
    cell = table.select(f"tbody tr:first-child td:nth-child({index})")[0]
    assert cell.string != None and len(cell.string) > 0, f"first tr of table cell {index} is empty"
    return cell.string.strip()

def query_and_get_assert(query, args, target, client, url):
    from ..sql.db import DB
    result = DB.selectAll(query, *args)
    if result.status and result.rows:
        n = result.rows[0][target]
        print("db result", n)
        resp = client.get(url)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.data, "html.parser")
        table = soup.table
        ths = table.select("thead tr th")
        
        columnIndex = get_column_index(target=target,cells=ths)
        cell_data = get_cell_content_by_index(columnIndex, table)
        print(cell_data)
        assert str(cell_data) == str(n)
    else:
        assert False



def test_filter_name(client):
    target = "name"
    query = f"SELECT id, {target} FROM IS601_MP2_Companies WHERE 1=1 AND {target} like %s ORDER BY name asc LIMIT 10"
    args = ["%a%"]
    url = f"/company/search?name={args[0].replace('%','')}&column=name&order=asc"
    query_and_get_assert(query=query, args=args, target=target, client=client, url=url)

def test_filter_country(client):
    target = "country"
    query = f"SELECT {target} FROM IS601_MP2_Employees e LEFT JOIN IS601_MP2_Companies c ON e.company_id = c.id WHERE {target} = %s LIMIT 10"
    args = ["US"]
    url = f"/company/search?country={args[0]}"
    query_and_get_assert(query=query, args=args, target=target, client=client, url=url)
    
def test_filter_state(client):
    target = "state"
    query = f"SELECT {target} FROM IS601_MP2_Employees e LEFT JOIN IS601_MP2_Companies c ON e.company_id = c.id WHERE {target} = %s LIMIT 10"
    args = ["NJ"]
    url = f"/company/search?state={args[0]}"
    query_and_get_assert(query=query, args=args, target=target, client=client, url=url)
 

def test_sort_asc_name(client):
    target = "name"
    order = "asc"
    query = f"SELECT {target} FROM IS601_MP2_Companies ORDER BY {target} {order} LIMIT 10"
    args = []
    url = f"/company/search?column={target}&order={order}"
    query_and_get_assert(query=query, args=args, target=target, client=client, url=url)

def test_sort_desc_name(client):
    target = "name"
    order = "desc"
    query = f"SELECT {target} FROM IS601_MP2_Companies ORDER BY {target} {order} LIMIT 10"
    args = []
    url = f"/company/search?column={target}&order={order}"
    query_and_get_assert(query=query, args=args, target=target, client=client, url=url)

def test_sort_asc_city(client):
    target = "city"
    order = "asc"
    query = f"SELECT {target} FROM IS601_MP2_Companies ORDER BY {target} {order} LIMIT 10"
    args = []
    url = f"/company/search?column={target}&order={order}"
    query_and_get_assert(query=query, args=args, target=target, client=client, url=url)

def test_sort_desc_city(client):
    target = "city"
    order = "desc"
    query = f"SELECT {target} FROM IS601_MP2_Companies ORDER BY {target} {order} LIMIT 10"
    args = []
    url = f"/company/search?column={target}&order={order}"
    query_and_get_assert(query=query, args=args, target=target, client=client, url=url)


def test_sort_asc_country(client):
    target = "country"
    order = "asc"
    query = f"SELECT {target} FROM IS601_MP2_Companies ORDER BY {target} {order} LIMIT 10"
    args = []
    url = f"/company/search?column={target}&order={order}"
    query_and_get_assert(query=query, args=args, target=target, client=client, url=url)

def test_sort_desc_country(client):
    target = "country"
    order = "desc"
    query = f"SELECT {target} FROM IS601_MP2_Companies ORDER BY {target} {order} LIMIT 10"
    args = []
    url = f"/company/search?column={target}&order={order}"
    query_and_get_assert(query=query, args=args, target=target, client=client, url=url)

def test_sort_asc_state(client):
    target = "state"
    order = "asc"
    query = f"SELECT {target} FROM IS601_MP2_Companies ORDER BY {target} {order} LIMIT 10"
    args = []
    url = f"/company/search?column={target}&order={order}"
    query_and_get_assert(query=query, args=args, target=target, client=client, url=url)

def test_sort_desc_state(client):
    target = "state"
    order = "desc"
    query = f"SELECT {target} FROM IS601_MP2_Companies ORDER BY {target} {order} LIMIT 10"
    args = []
    url = f"/company/search?column={target}&order={order}"
    query_and_get_assert(query=query, args=args, target=target, client=client, url=url)

def test_employee_count(client):
    target = "employees"
    args = []
    query = """SELECT name,
    (SELECT count(1) FROM IS601_MP2_Employees e where e.company_id = IS601_MP2_Companies.id) as employees 
    FROM IS601_MP2_Companies ORDER BY RAND() LIMIT 1"""
    from ..sql.db import DB
    result = DB.selectOne(query, *args)
    if result.status and result.row:
        name = result.row["name"]
        count = int(result.row["employees"])
        print("expected count", count)
        query = """SELECT
    (SELECT count(1) FROM IS601_MP2_Employees e where e.company_id = IS601_MP2_Companies.id) as employees 
    FROM IS601_MP2_Companies where name = %s LIMIT 1"""
        args = [name]
        import urllib.parse
        url = f"/company/search?name={urllib.parse.quote_plus(args[0])}"
        query_and_get_assert(query=query, args=args, target=target, client=client, url=url)
        return
    assert False