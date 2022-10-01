"""Test machinery common to all gallery examples."""
import pytest
from bs4 import element
from playwright.sync_api import Page
from starlette.testclient import TestClient

from psc.fixtures import PageT


def test_hello_world(client_page: PageT) -> None:
    """Test the static HTML for Hello World."""
    soup = client_page("/gallery/examples/hello_world/")

    # Title and subtitle
    title = soup.select_one("title")
    assert title
    assert title.text == "Hello World | PyScript Collective"
    subtitle = soup.select_one('meta[name="subtitle"]')
    assert subtitle
    assert (
        subtitle.get("content")
        == "The classic hello world, but in Python -- in a browser!"
    )

    # See if extra_head got filled, then resolve those
    assert soup.find_all("link", href="hello_world.css")
    assert soup.find_all("script", src="hello_world.js")

    # Ensure the ``<main>`` got filled
    assert soup.select_one("main")

    # Only one <py-config>, pointing to local runtime
    py_configs = soup.select("py-config")
    assert len(py_configs) == 1

    # The <py-script> is present
    py_scripts = soup.select("py-script")
    assert len(py_scripts) == 1


def test_hello_world_js(test_client: TestClient) -> None:
    """Test the static assets for Hello World."""
    response = test_client.get("/gallery/examples/hello_world/hello_world.js")
    assert response.status_code == 200


#
#
# @pytest.mark.full
# def test_hello_world_full(fake_page: Page) -> None:
#     """Use Playwright to do a test on Hello World."""
#     # Use `PWDEBUG=1` to run "head-ful" in Playwright test app
#     url = "http://fake/gallery/examples/hello_world/index.html"
#     fake_page.goto(url)
#     title = fake_page.title()
#     assert title == "Hello World Python"
