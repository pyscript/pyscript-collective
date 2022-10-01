"""Test the views for the Page resource."""
from psc.fixtures import PageT


def test_about_page(client_page: PageT) -> None:
    """Use the navbar to get the link to the about page."""
    index_soup = client_page("/")
    about_link = index_soup.select_one("#navbarAbout")
    assert about_link
    about_href = about_link.get("href")
    assert about_href
    about_soup = client_page(about_href)
    assert about_soup

    # Page title/subtitle
    page_title = about_soup.select_one("title")
    assert page_title
    assert page_title.text == "About the PyScript Collective | PyScript Collective"
    subtitle = about_soup.select_one(".subtitle")
    assert subtitle and (
        subtitle.text
        == "The mission, background, and moving parts about the Collective."
    )

    # Page body
    em = about_soup.select_one("main em")
    assert em
    assert em.text == "share"


def test_contributing_page(client_page: PageT) -> None:
    """Loading a Page defined as html works fine."""
    soup = client_page("/pages/contributing.html")
    page_title = soup.select_one("title")
    assert page_title and "Contributing | PyScript Collective" == page_title.text
