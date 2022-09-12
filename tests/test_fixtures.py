"""Ensure the test fixtures work as expected."""
from typing import cast

import pytest
from bs4 import BeautifulSoup
from playwright.sync_api import Page
from playwright.sync_api import Route
from starlette.testclient import TestClient

from psc.here import STATIC
from psc.fixtures import DummyPage
from psc.fixtures import DummyRequest
from psc.fixtures import DummyResponse
from psc.fixtures import DummyRoute
from psc.fixtures import MockTestClient
from psc.fixtures import PageT
from psc.fixtures import mocked_client_page
from psc.fixtures import route_handler


def test_test_client(test_client: TestClient) -> None:
    """Ensure fixture returns an initialized TestClient."""
    assert test_client.app


def test_mock_test_client() -> None:
    """Ensure the mock obeys the contract."""
    mtc = MockTestClient()
    assert mtc.test_status_code == 200
    response = mtc.get("/index")
    assert mtc.test_url == "/index"
    assert response.status_code == 200
    assert response.content == b"Test Result"


def test_mock_test_client_broken() -> None:
    """Ensure the mock can trigger a 404."""
    mtc = MockTestClient()
    response = mtc.get("/broken")
    assert response.status_code == 404


def test_valid_url_not_mocked(client_page: PageT) -> None:
    """Use actual TestClient to get index_page route and ensure soup."""
    soup = client_page("/")
    assert isinstance(soup, BeautifulSoup)


def test_invalid_url_not_mocked(client_page: PageT) -> None:
    """Use actual TestClient to get index_page route and ensure soup."""
    with pytest.raises(ValueError) as exc:
        client_page("/xxx")
    assert str(exc.value) == "Request to /xxx resulted in status code 404"


def test_valid_url_mocked() -> None:
    """Use fake TestClient to get index_page route and ensure soup."""
    page = mocked_client_page()
    soup = page("/")
    assert isinstance(soup, BeautifulSoup)


def test_invalid_url_mocked() -> None:
    """Use fake TestClient to get index_page route and ensure soup."""
    page = mocked_client_page()
    with pytest.raises(ValueError) as exc:
        page("/broken")
    assert str(exc.value) == "Request to /broken resulted in status code 404"


def test_dummy_request() -> None:
    """Ensure the fake Playwright request class works."""
    dummy_request = DummyRequest(url="/dummy")
    result = dummy_request.fetch(dummy_request)
    assert result.dummy_text == "URL Returned Text"


def test_dummy_response() -> None:
    """Ensure the fake Playwright response class works."""
    dummy_response = DummyResponse(dummy_text="test dummy response")
    assert dummy_response.text() == "test dummy response"
    assert dummy_response.body() == b"test dummy response"
    assert dummy_response.headers["Content-Type"] == "text/html"


def test_dummy_route() -> None:
    """Ensure the fake Playwright route class works."""
    dummy_request = DummyRequest(url="/dummy")
    dummy_route = DummyRoute(request=dummy_request)
    dummy_route.fulfill(
        body=b"dummy body", headers={"Content-Type": "text/html"}, status=200
    )
    assert dummy_route.body == b"dummy body"
    assert dummy_route.headers["Content-Type"] == "text/html"  # type: ignore


def test_route_handler_fake_good_path() -> None:
    """Fake points at good path in ``examples``."""
    # We are testing the interceptor, because the hostname is "fake".
    dummy_request = DummyRequest(url="https://fake/static/bulma.min.css")
    dummy_page = DummyPage(request=dummy_request)
    dummy_route = DummyRoute(request=dummy_request)
    route_handler(
        cast(Page, dummy_page),
        cast(Route, dummy_route),
    )
    if dummy_route.body:
        assert dummy_route.status == "200"
        with open(STATIC / "bulma.min.css", "rb") as f:
            body = f.read()
            assert dummy_route.body == body


def test_route_handler_non_fake() -> None:
    """Not fake thus not interceptor, but simulating network request."""
    dummy_request = DummyRequest(url="https://good/static/bulma.min.css")
    dummy_page = DummyPage(request=dummy_request)
    dummy_route = DummyRoute(request=dummy_request)
    route_handler(
        cast(Page, dummy_page),
        cast(Route, dummy_route),
    )
    assert dummy_route.body == b"URL Returned Text"


def test_route_handler_fake_bad_path() -> None:
    """Fake points at bad path in ``examples``."""
    dummy_request = DummyRequest(url="https://fake/staticxx")
    dummy_page = DummyPage(request=dummy_request)
    dummy_route = DummyRoute(request=dummy_request)
    route_handler(
        cast(Page, dummy_page),
        cast(Route, dummy_route),
    )
    assert dummy_route.status == "404"
