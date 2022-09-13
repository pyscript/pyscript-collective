"""Test the Starlette web app for browsing examples."""
from starlette.testclient import TestClient

from psc.fixtures import PageT


def test_index_page(client_page: PageT) -> None:
    """See if the HTML returned by the home page matches expectations."""
    soup = client_page("/")
    p = soup.select_one("title")
    if p:
        assert p.text == "Home Page | PyScript Collective"
    main = soup.select_one("main")
    assert main


def test_bulma_css(client_page: PageT, test_client: TestClient) -> None:
    """Get the home page, find the stylesheet link to Bulma, ensure it returns."""
    soup = client_page("/")
    stylesheet = soup.select_one("link[rel='stylesheet']")
    if stylesheet:
        href = stylesheet.attrs["href"]
        assert href == "/static/bulma.min.css"
        response = test_client.get(href)
        assert response.status_code == 200


def test_favicon(test_client: TestClient) -> None:
    """Ensure the app provides a favicon route."""
    response = test_client.get("/favicon.png")
    assert response.status_code == 200


def test_examples(test_client: TestClient) -> None:
    """Ensure the app provides an /examples/ route."""
    response = test_client.get("/examples/hello_world/index.html")
    assert response.status_code == 200


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
