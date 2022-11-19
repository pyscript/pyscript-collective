"""Automate some testing."""
from __future__ import annotations

import builtins
from collections.abc import Callable
from collections.abc import Generator
from collections.abc import Iterable
from dataclasses import dataclass
from dataclasses import field
from mimetypes import guess_type
from urllib.parse import urlparse

import pytest
from bs4 import BeautifulSoup
from playwright.sync_api import Page
from playwright.sync_api import Route
from requests.models import Response
from starlette.testclient import TestClient

from psc.app import app
from psc.here import HERE


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
def test_client() -> Generator[TestClient, None, None]:
    """Return the app in a context manager to allow lifecyle to run."""
    with TestClient(app) as client:
        yield client


def _base_page(client: TestClient | MockTestClient) -> PageT:
    """Automate ``TestClient`` to return BeautifulSoup.

    Default to raising an exception if the status code isn't 200.
    """

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

    return page


@dataclass
class FakeDocument:
    """Pretend to be a DOM that holds values at id's."""

    values: dict[str, str] = field(default_factory=dict)
    log: list[str] = field(default_factory=list)
    nodes: dict[str, FakeElement] = field(default_factory=dict)


@pytest.fixture
def fake_document() -> Iterable[FakeDocument]:
    """Yield a document that cleans up."""
    yield FakeDocument()


@dataclass
class FakeElementNode:
    """Fake for PyScript's ``element`` accessor that gets DOM node."""

    log: list[str] = field(default_factory=list)

    def removeAttribute(self, name: str) -> None:  # noqa
        """Pretend to remove an attribute from this node."""
        self.log.append(f"Removed {name}")


@dataclass
class FakeElement:
    """A fake for PyScript's Element global."""

    value: str
    document: FakeDocument
    element: FakeElementNode = FakeElementNode()

    def write(self, value: str) -> None:
        """Collect anything that is written to the node."""
        self.document.log.append(value)


@dataclass
class ElementCallable:
    """A callable that registers and returns an ElementNode."""

    document: FakeDocument

    def __call__(self, key: str) -> FakeElement:
        """Return an ElementNode."""
        value = self.document.values[key]
        node = FakeElement(value, self.document)
        self.document.nodes[key] = node
        return node

    def removeAttribute(self, attr: str) -> None:  # noqa: N802
        """Fake the remove attribute call."""
        pass

    def write(self, content: str) -> None:
        """Fake the write call."""
        pass


@pytest.fixture
def fake_element(fake_document: FakeDocument) -> ElementCallable:  # type: ignore [misc]
    """Install the stateful Element into builtins."""
    try:
        this_element = ElementCallable(fake_document)
        builtins.Element = this_element  # type: ignore [attr-defined]
        yield this_element
    finally:
        delattr(builtins, "Element")
