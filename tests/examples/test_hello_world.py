"""Test the ``Hello World`` example."""
import pytest
from playwright.sync_api import Page

from psc.fixtures import PageT


def test_hello_world(client_page: PageT) -> None:
    """Test the static HTML for Hello World."""
    soup = client_page("/examples/hello_world/index.html")
    title = soup.select_one("title")
    if title:
        assert title.text == "PyScript Hello World"


@pytest.mark.full
def test_hello_world_full(fake_page: Page) -> None:
    """Use Playwright to do a test on Hello World."""
    fake_page.goto("http://fake/examples/hello_world/index.html")
    assert fake_page.title() == "PyScript Hello World"
    # Turn this on when using `PWDEBUG=1` to run "head-ful"
    # fake_page.pause()
    element = fake_page.wait_for_selector("text=...world")
    if element:
        assert element.text_content() == "...world"
