"""Test the Starlette web app for browsing examples."""

from psc.fixtures import PageT


def test_index_page(client_page: PageT) -> None:
    """See if the HTML returned by the home page matches expectations."""
    soup = client_page("/")
    p = soup.select_one("title")
    if p:
        assert p.text == "Custom Elements"
