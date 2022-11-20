"""Test machinery common to all gallery examples."""
from starlette.testclient import TestClient

from psc.fixtures import PageT


def test_hello_world(client_page: PageT) -> None:
    """Test the static HTML for Hello World."""
    soup = client_page("/gallery/examples/hello_world/")

    # Title and subtitle
    title = soup.select_one("title")
    assert title and title.text == "Hello World | PyScript Collective"
    subtitle = soup.select_one('meta[name="subtitle"]')
    assert subtitle
    assert (
        subtitle.get("content")
        == "The classic hello world, but in Python -- in a browser!"
    )

    # See if extra_head got filled, then resolve those
    assert soup.find_all("link", href="hello_world.css")

    # Ensure the ``<main>`` got filled
    assert soup.select_one("main")

    # Only one <py-config>, pointing to local runtime
    py_configs = soup.select("py-config")
    assert len(py_configs) == 1

    # The <py-script> is present
    py_scripts = soup.select("py-script")
    assert len(py_scripts) == 1

    # Back to code button
    button = soup.select_one("a.is-pulled-right")
    assert button and "Show Code" == button.text


def test_hello_world_js(test_client: TestClient) -> None:
    """Test the static assets for Hello World."""
    response = test_client.get("/gallery/examples/hello_world/hello_world.js")
    assert response.status_code == 200


def test_hello_world_code(client_page: PageT) -> None:
    """Test code samples for hello world example."""
    soup = client_page("/gallery/examples/hello_world/code.html")
    title = soup.select_one("title")
    assert title
    assert "Hello World Code | PyScript Collective" == title.text.strip()
    linked_file_heading = soup.select_one("h2")
    assert linked_file_heading
    assert "index.html" == linked_file_heading.text

    # Back to code button
    button = soup.select_one("a.is-pulled-right")
    assert button and "Back to Demo" == button.text
