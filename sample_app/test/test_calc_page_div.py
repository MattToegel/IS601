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




def test_post_div(client):
    response = client.post("/mycalc/", data={"eq": "4/2"})
    html = response.data.decode("UTF-8")
    # string to soup
    soup = BeautifulSoup(html, 'html.parser')
    # find the <input> tag with id "result"
    result_ele = soup.find(id="result")
    # get the value attribute of the input tag
    assert result_ele.get("value") == "2"

# https://www.twilio.com/blog/web-scraping-and-parsing-html-in-python-with-beautiful-soup
# https://www.crummy.com/software/BeautifulSoup/bs4/doc/
# https://stackabuse.com/convert-bytes-to-string-in-python/
