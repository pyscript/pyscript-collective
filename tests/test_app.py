"""Test the Starlette web app for browsing examples."""
from starlette.testclient import TestClient

from psc.app import app


def test_index_page() -> None:
    """Test the view for the index route."""
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
