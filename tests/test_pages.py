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

    # Page title
    page_title = about_soup.select_one("title")
    assert page_title
    assert page_title.text == "About PyScript Collective | PyScript Collective"

    # Page body
    em = about_soup.select_one("main em")
    assert em
    assert em.text == "is here"
