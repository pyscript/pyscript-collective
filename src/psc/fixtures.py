"""Automate some testing."""
from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from mimetypes import guess_type
from typing import Callable
from urllib.parse import urlparse

import pytest
from bs4 import BeautifulSoup
from playwright.sync_api import Page
from playwright.sync_api import Route
from requests.models import Response
from starlette.testclient import TestClient

from psc.here import HERE
from psc.app import app


@dataclass
class MockTestClient:
    """Pretend to be Starlette ``TestClient``."""

    test_status_code: int = 200
    test_url: str | None = None
    test_content: bytes | None = None

    def get(self, url: str) -> Response:
        """Fake the TestClient response getting."""
        self.test_url = url
        response = Response()
        if self.test_url == "/broken":
            # This is a flag to test base_page exception raising
            response.status_code = 404
        else:
            response.status_code = self.test_status_code
        response._content = (
            self.test_content if self.test_content is not None else b"Test Result"
        )
        return response


PageT = Callable[..., BeautifulSoup]


@pytest.fixture
def test_client() -> TestClient:
    """Get a TestClient for the app."""
    return TestClient(app)


def _base_page(client: TestClient | MockTestClient) -> PageT:
    """Automate ``TestClient`` to return BeautifulSoup.

    Along the way, default to raising an exception if the status
    code isn't 200.
    """
    # Allow passing in a fake TestClient, for testing this fixture.

    def _page(url: str, *, enforce_status: bool = True) -> BeautifulSoup:
        """Callable that retrieves and returns soup."""
        response = client.get(url)
        if enforce_status and response.status_code != 200:
            raise ValueError(
                f"Request to {url} resulted in status code {response.status_code}"
            )
        return BeautifulSoup(response.text, "html5lib")

    return _page


def mocked_client_page() -> PageT:
    """Get a fake test client, to allow testing the logic in base_page."""
    client = MockTestClient()
    return _base_page(client)


@pytest.fixture()
def client_page(test_client: TestClient) -> PageT:
    """Main fixture for getting BeautifulSoup via TestClient."""
    return _base_page(test_client)


@dataclass
class DummyResponse:
    """Fake the Playwright ``Response`` class."""

    dummy_text: str = ""
    headers: dict[str, object] = field(
        default_factory=lambda: {"Content-Type": "text/html"}
    )
    status: int | None = None

    def text(self) -> str:
        """Fake the text method."""
        return self.dummy_text

    def body(self) -> bytes:
        """Fake the text method."""
        return bytes(self.dummy_text, "utf-8")


@dataclass
class DummyRequest:
    """Fake the Playwright ``Request`` class."""

    url: str

    @staticmethod
    def fetch(request: DummyRequest) -> DummyResponse:
        """Fake the fetch method."""
        return DummyResponse(dummy_text="URL Returned Text")


@dataclass
class DummyRoute:
    """Fake the Playwright ``Route`` class."""

    request: DummyRequest
    body: bytes | None = None
    status: str | None = None
    headers: dict[str, object] | None = None

    def fulfill(self, body: bytes, headers: dict[str, object], status: int) -> None:
        """Stub the Playwright ``route.fulfill`` method."""
        self.body = body
        self.headers = headers
        self.status = str(status)


@dataclass
class DummyPage:
    """Fake the Playwright ``Page`` class."""

    request: DummyRequest


def route_handler(page: Page, route: Route) -> None:
    """Called from the interceptor to get the data off disk."""
    this_url = urlparse(route.request.url)
    this_path = this_url.path[1:]
    is_fake = this_url.hostname == "fake"
    headers = dict()
    if is_fake:
        # We should read something from the filesystem
        this_fs_path = HERE / this_path
        if this_fs_path.exists():
            status = 200
            mime_type = guess_type(this_fs_path)[0]
            if mime_type:
                headers = {"Content-Type": mime_type}
            body = this_fs_path.read_bytes()
        else:
            status = 404
            body = b""
    else:
        # This is to a non-fake server. Only for cases where the
        # local HTML asked for something out in the big wide world.
        response = page.request.fetch(route.request)
        status = response.status
        body = response.body()
        headers = response.headers

    route.fulfill(body=body, headers=headers, status=status)


@pytest.fixture
def fake_page(page: Page) -> Page:  # pragma: no cover
    """On the fake server, intercept and return from fs."""

    def _route_handler(route: Route) -> None:
        """Instead of doing this inline, call to a helper for easier testing."""
        route_handler(page, route)

    # Use Playwright's route method to intercept any URLs pointed at the
    # fake server and run through the interceptor instead.
    page.route("**", _route_handler)

    # Don't spend 30 seconds on timeout
    page.set_default_timeout(8000)
    return page
