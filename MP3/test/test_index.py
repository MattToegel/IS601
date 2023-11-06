import pytest
from bs4 import BeautifulSoup
@pytest.fixture(scope='module')
def app():
    from ..main import create_app
    app = create_app()
    """app.config.update({
        "TESTING": True,
    })"""

    # other setup can go here

    yield app

    # clean up / reset resources here


@pytest.fixture(scope='module')
def client(app):
    return app.test_client()

@pytest.fixture(scope='module')
def index(client):
    resp = client.get("/")
    soup = BeautifulSoup(resp.data, "html.parser")
    return soup
@pytest.fixture(scope='module')
def btyb(index):
    return index.select_one(".btyb")

def test_btyb_exists(btyb):
    print(f"{btyb}")
    assert btyb, "Missing 'brought to you by' section" 
def test_replaced_my_ucid(btyb):
    assert '(mt85)' not in btyb.text, "My ucid was not replaced"
def test_placed_course_section(btyb):
    assert 'IS601-000' not in btyb.text, "Course/section was not replaced"