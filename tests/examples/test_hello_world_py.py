"""Test the ``Hello World`` in Python file example."""
import builtins
from dataclasses import dataclass
from typing import cast

import pytest
from playwright.sync_api import Page

from psc.fixtures import PageT


def test_hello_world(client_page: PageT) -> None:
    """Test the static HTML for Hello World."""
    soup = client_page("/gallery/examples/hello_world_py/")
    title = soup.select_one("title")
    assert title and title.text == "Hello World Python | PyScript Collective"


@dataclass
class FakeElement:
    """Stub out the usage of PyScript's injected Element."""

    target_name: str
    result: str | None = None

    def write(self, value: str) -> None:
        """Store what you were told to display."""
        self.result = value


def test_hello_world_python() -> None:
    """Unit test the hello_world.py that is loaded."""
    try:
        builtins.Element = FakeElement
        from psc.gallery.examples.hello_world_py.hello_world import output
    finally:
        delattr(builtins, "Element")

    assert cast(FakeElement, output).result == "From Python..."


@pytest.mark.full
def test_hello_world_full(fake_page: Page) -> None:
    """Use Playwright to do a test on Hello World."""
    # Use `PWDEBUG=1` to run "head-ful" in Playwright test app
    url = "http://fake/gallery/examples/hello_world_py/index.html"
    fake_page.goto(url)
    assert fake_page.title() == "Hello World Python"
    element = fake_page.wait_for_selector("text=From Python...")
    if element:
        assert element.text_content() == "From Python..."
