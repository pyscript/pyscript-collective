"""Test the Starlette web app for browsing examples."""
from starlette.testclient import TestClient

from psc.fixtures import PageT


def test_index_page(client_page: PageT) -> None:
    """See if the HTML returned by the home page matches expectations."""
    soup = client_page("/")

    # Title and main
    title = soup.select_one("title")
    if title:
        assert title.text == "Home Page | PyScript Collective"
    section = soup.select_one("section")
    assert section


def test_bulma_css(client_page: PageT, test_client: TestClient) -> None:
    """Get the home page, find the stylesheet link to Bulma, ensure it returns."""
    soup = client_page("/")
    stylesheet = soup.select_one("link[rel='stylesheet']")
    if stylesheet:
        href = stylesheet.attrs["href"]
        assert href == "./static/psc.css"
        response = test_client.get(href)
        assert response.status_code == 200


def test_favicon(test_client: TestClient) -> None:
    """Ensure the app provides a favicon route."""
    response = test_client.get("/favicon.png")
    assert response.status_code == 200


def test_examples_listing(client_page: PageT) -> None:
    """Ensure the route lists the examples."""
    # First get the URL from the navbar.
    index_soup = client_page("/")
    nav_examples = index_soup.select_one("#navbarGallery")
    assert nav_examples
    examples_href = nav_examples.get("href")
    assert examples_href
    examples_soup = client_page(examples_href)
    assert examples_soup

    # Example title
    examples_title = examples_soup.select_one("title")
    assert examples_title
    assert examples_title.text == "Gallery | PyScript Collective"

    # Example subtitle
    subtitle = examples_soup.select_one("p.subtitle")
    assert subtitle
    assert "Curated" in subtitle.text

    # Example description
    description_em = examples_soup.select_one("div.content em")
    assert description_em
    assert description_em.text == "hello world"

    # Get the first example, follow the link, ensure it is Hello World
    first_example = examples_soup.select_one("p.title a")
    assert first_example
    first_href = first_example.get("href")
    assert first_href == "../gallery/examples/hello_world/"
    hello_soup = client_page(first_href)
    assert hello_soup
    title = hello_soup.select_one("title")
    assert title
    assert title.text == "Hello World | PyScript Collective"


def test_static(test_client: TestClient) -> None:
    """Ensure the app provides a /static/ route."""
    response = test_client.get("/static/bulma.min.css")
    assert response.status_code == 200


def test_pyscript(test_client: TestClient) -> None:
    """Ensure the app provides a path to the ``pyscript`` static dir."""
    response = test_client.get("/pyscript/pyscript.js")
    assert response.status_code == 200


def test_pyodide(test_client: TestClient) -> None:
    """Ensure the app provides a path to the ``pyodide`` static dir."""
    response = test_client.get("/pyodide/pyodide.js")
    assert response.status_code == 200
