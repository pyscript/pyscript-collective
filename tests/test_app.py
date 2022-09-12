"""Test the Starlette web app for browsing examples."""
from starlette.testclient import TestClient

from psc.fixtures import PageT


def test_index_page(client_page: PageT) -> None:
    """See if the HTML returned by the home page matches expectations."""
    soup = client_page("/")
    p = soup.select_one("title")
    if p:
        assert p.text == "Custom Elements"


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
