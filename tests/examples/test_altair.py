"""Test the ``Altair`` example."""
import pytest
from playwright.sync_api import Page

from psc.fixtures import PageT


def test_altair(client_page: PageT) -> None:
    """Test the static HTML for Altair."""
    soup = client_page("/gallery/examples/altair/")
    title = soup.select_one("title")
    assert title and title.text == "Altair Visualization | PyScript Collective"


@pytest.mark.full
def test_altair_full(fake_page: Page) -> None:
    """Use Playwright to do a test on Altair."""
    # Use `PWDEBUG=1` to run "head-ful" in Playwright test app
    url = "http://fake/gallery/examples/altair/index.html"
    fake_page.goto(url)
    assert fake_page.title() == "Altair Visualization"
    element = fake_page.wait_for_selector(".chart-wrapper")
    if element:
        assert element.get_attribute("role") == "graphics-document"
