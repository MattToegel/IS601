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
    return cell.string

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
        assert cell_data == n
    else:
        assert False



def test_filter_fn(client):
    target = "first_name"
    query = f"SELECT {target} FROM IS601_MP2_Employees e LEFT JOIN IS601_MP2_Companies c ON e.company_id = c.id WHERE {target} like %s LIMIT 10"
    args = ["%a%"]
    url = f"/employee/search?fn={args[0].replace('%','')}"
    query_and_get_assert(query=query, args=args, target=target, client=client, url=url)

def test_filter_ln(client):
    target = "last_name"
    query = f"SELECT {target} FROM IS601_MP2_Employees e LEFT JOIN IS601_MP2_Companies c ON e.company_id = c.id WHERE {target} like %s LIMIT 10"
    args = ["%v%"]
    url = f"/employee/search?ln={args[0].replace('%','')}"
    query_and_get_assert(query=query, args=args, target=target, client=client, url=url)
    

def test_filter_email(client):
    target = "email"
    query = f"SELECT {target} FROM IS601_MP2_Employees e LEFT JOIN IS601_MP2_Companies c ON e.company_id = c.id WHERE {target} like %s LIMIT 10"
    args = ["%.net%"]
    url = f"/employee/search?email={args[0].replace('%','')}"
    query_and_get_assert(query=query, args=args, target=target, client=client, url=url)


def test_filter_company(client):
    from ..sql.db import DB
    result = DB.selectOne("SELECT id FROM IS601_MP2_Companies ORDER BY RAND() LIMIT 1")
    args = [2]
    if result.status and result.row:
        args[0] = int(result.row["id"])
    query = "SELECT IF(name is not null, name,'N/A') as company_name FROM IS601_MP2_Employees e JOIN IS601_MP2_Companies c ON e.company_id = c.id WHERE e.company_id = %s LIMIT 10"
    target = "company_name"
    url = f"/employee/search?company={args[0]}"
    query_and_get_assert(query=query, args=args, target=target, client=client, url=url)


def test_sort_asc_fn(client):
    target = "first_name"
    order = "asc"
    query = f"SELECT {target} FROM IS601_MP2_Employees e LEFT JOIN IS601_MP2_Companies c ON e.company_id = c.id ORDER BY {target} {order} LIMIT 10"
    args = []
    url = f"/employee/search?column={target}&order={order}"
    query_and_get_assert(query=query, args=args, target=target, client=client, url=url)

def test_sort_desc_fn(client):
    target = "first_name"
    order = "desc"
    query = f"SELECT {target} FROM IS601_MP2_Employees e LEFT JOIN IS601_MP2_Companies c ON e.company_id = c.id ORDER BY {target} {order} LIMIT 10"
    args = []
    url = f"/employee/search?column={target}&order={order}"
    query_and_get_assert(query=query, args=args, target=target, client=client, url=url)

def test_sort_asc_ln(client):
    target = "last_name"
    order = "asc"
    query = f"SELECT {target} FROM IS601_MP2_Employees e LEFT JOIN IS601_MP2_Companies c ON e.company_id = c.id ORDER BY {target} {order} LIMIT 10"
    args = []
    url = f"/employee/search?column={target}&order={order}"
    query_and_get_assert(query=query, args=args, target=target, client=client, url=url)

def test_sort_desc_ln(client):
    target = "last_name"
    order = "desc"
    query = f"SELECT {target} FROM IS601_MP2_Employees e LEFT JOIN IS601_MP2_Companies c ON e.company_id = c.id ORDER BY {target} {order} LIMIT 10"
    args = []
    url = f"/employee/search?column={target}&order={order}"
    query_and_get_assert(query=query, args=args, target=target, client=client, url=url)

def test_sort_asc_email(client):
    target = "email"
    order = "asc"
    query = f"SELECT {target} FROM IS601_MP2_Employees e LEFT JOIN IS601_MP2_Companies c ON e.company_id = c.id ORDER BY {target} {order} LIMIT 10"
    args = []
    url = f"/employee/search?column={target}&order={order}"
    query_and_get_assert(query=query, args=args, target=target, client=client, url=url)

def test_sort_desc_email(client):
    target = "email"
    order = "desc"
    query = f"SELECT {target} FROM IS601_MP2_Employees e LEFT JOIN IS601_MP2_Companies c ON e.company_id = c.id ORDER BY {target} {order} LIMIT 10"
    args = []
    url = f"/employee/search?column={target}&order={order}"
    query_and_get_assert(query=query, args=args, target=target, client=client, url=url)

def test_sort_asc_company(client):
    target = "company_name"
    order = "asc"
    query = f"SELECT IF(name is not null, name,'N/A') as company_name FROM IS601_MP2_Employees e LEFT JOIN IS601_MP2_Companies c ON e.company_id = c.id ORDER BY {target} {order} LIMIT 10"
    args = []
    url = f"/employee/search?column={target}&order={order}"
    query_and_get_assert(query=query, args=args, target=target, client=client, url=url)

def test_sort_desc_company(client):
    target = "company_name"
    order = "desc"
    query = f"SELECT IF(name is not null, name,'N/A') as company_name FROM IS601_MP2_Employees e LEFT JOIN IS601_MP2_Companies c ON e.company_id = c.id ORDER BY {target} {order} LIMIT 10"
    args = []
    url = f"/employee/search?column={target}&order={order}"
    query_and_get_assert(query=query, args=args, target=target, client=client, url=url)