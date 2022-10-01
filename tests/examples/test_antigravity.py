"""Test the ``Antigravity`` example."""
import pytest
from playwright.sync_api import Page

from psc.fixtures import PageT


def test_antigravity(client_page: PageT) -> None:
    """Test the static HTML for Antigravity."""
    soup = client_page("/gallery/examples/antigravity/")
    title = soup.select_one("title")
    assert title and title.text == "xkcd Antigravity | PyScript Collective"


@pytest.mark.full
def test_antigravity_full(fake_page: Page) -> None:
    """Use Playwright to do a test on Antigravity."""
    # Use `PWDEBUG=1` to run "head-ful" in Playwright test app
    url = "http://fake/gallery/examples/antigravity/index.html"
    fake_page.goto(url)
    assert fake_page.title() == "xkcd Antigravity"
    element = fake_page.wait_for_selector("#svg8")
    if element:
        assert element.get_attribute("id") == "svg8"
