"""Test the ``Antigravity`` example."""

import pytest
from playwright.sync_api import Page

from psc.fixtures import PageT


def test_calculator(fake_document, fake_element) -> None:
    """Ensure the loaded interest function works correctly."""
    from psc.gallery.examples.interest_calculator.calculator import interest

    fake_document.values["principal"] = "100"
    fake_document.values["interest_rate"] = "0.1"
    fake_document.values["time"] = "10"
    fake_document.values["simple_interest"] = "0.1"
    fake_document.values["compound_interest"] = "0.1"
    interest()
    assert fake_document.log[0] == "simple interest: 200"
    assert fake_document.log[1] == "compound interest: 259"


def test_interest_calculator(client_page: PageT) -> None:
    """Test the static HTML for Antigravity."""
    soup = client_page("/gallery/examples/interest_calculator/")
    title = soup.select_one("title")
    assert title and title.text == "Compound Interest Calculator | PyScript Collective"


@pytest.mark.full
def test_interest_calculator_full(fake_page: Page) -> None:
    """Use Playwright to do a test on Antigravity."""
    # Use `PWDEBUG=1` to run "head-ful" in Playwright test app
    url = "http://fake/gallery/examples/interest_calculator/index.html"
    fake_page.goto(url)
    assert fake_page.title() == "Interest Calculator"
    button = fake_page.wait_for_selector("#calc:enabled")
    fake_page.get_by_text("Principal").fill("1000")
    fake_page.get_by_text("Interest rate").fill("0.1")
    fake_page.get_by_text("Time").fill("10")
    si = fake_page.query_selector("#simple_interest")
    ci = fake_page.query_selector("#compound_interest")
    button.click()
    assert si.text_content() == "simple interest: 2000"
    assert ci.text_content() == "compound interest: 2594"
