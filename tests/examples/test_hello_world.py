"""Test the ``Hello World`` example."""
import pytest
from playwright.sync_api import Page

from psc.fixtures import PageT


def test_hello_world(client_page: PageT) -> None:
    """Test the static HTML for Hello World."""
    soup = client_page("/gallery/examples/hello_world/")
    title = soup.select_one("title")
    assert title and title.text == "Hello World | PyScript Collective"


@pytest.mark.full
def test_hello_world_full(fake_page: Page) -> None:
    """Use Playwright to do a test on Hello World."""
    # Use `PWDEBUG=1` to run "head-ful" in Playwright test app
    url = "http://fake/gallery/examples/hello_world/index.html"
    fake_page.goto(url)
    assert fake_page.title() == "Hello World"
    element = fake_page.wait_for_selector("text=...world")
    if element:
        assert element.text_content() == "...world"
