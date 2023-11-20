import pytest
from bs4 import BeautifulSoup


@pytest.fixture()
def app():
    from ..main import create_app
    app = create_app()
    """app.config.update({
        "TESTING": True,
    })"""

    # other setup can go here

    yield app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_post_add_basic(client):
    response = client.post("/mycalc/", data={"eq": "7+7"})
    print(response.data)
    assert b"value=\"14\"" in response.data


def test_post_add(client):
    response = client.post("/mycalc/", data={"eq": "7+7"})
    html = response.data.decode("UTF-8")
    # string to soup
    soup = BeautifulSoup(html, 'html.parser')
    # find the <input> tag with id "result"
    result_ele = soup.find(id="result")
    v = result_ele.get("value")
    print("Result is " + str(v))
    # get the value attribute of the input tag
    assert v == "14"

def test_post_sub(client):
    response = client.post("/mycalc/", data={"eq": "10-4"})
    html = response.data.decode("UTF-8")
    # string to soup
    soup = BeautifulSoup(html, 'html.parser')
    # find the <input> tag with id "result"
    result_ele = soup.find(id="result")
    v = result_ele.get("value")
    print("Result is " + str(v))
    # get the value attribute of the input tag
    assert v == "6"

def test_post_mult(client):
    response = client.post("/mycalc/", data={"eq": "4*4"})
    html = response.data.decode("UTF-8")
    # string to soup
    soup = BeautifulSoup(html, 'html.parser')
    # find the <input> tag with id "result"
    result_ele = soup.find(id="result")
    v = result_ele.get("value")
    print("Result is " + str(v))
    # get the value attribute of the input tag
    assert v == "16"

def test_post_div(client):
    response = client.post("/mycalc/", data={"eq": "4/2"})
    html = response.data.decode("UTF-8")
    # string to soup
    soup = BeautifulSoup(html, 'html.parser')
    # find the <input> tag with id "result"
    result_ele = soup.find(id="result")
    # get the value attribute of the input tag
    v = result_ele.get("value")
    print("Result is " + str(v))
    assert v == "2.0"
# https://www.twilio.com/blog/web-scraping-and-parsing-html-in-python-with-beautiful-soup
# https://www.crummy.com/software/BeautifulSoup/bs4/doc/
# https://stackabuse.com/convert-bytes-to-string-in-python/
