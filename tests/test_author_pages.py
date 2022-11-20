"""Use the routes to render listing of authors and each one."""
from psc.fixtures import PageT


def test_authors_page(client_page: PageT) -> None:
    """The listing of authors works."""
    soup = client_page("/authors/index.html")
    page_title = soup.select_one("title")
    assert page_title and "Authors | PyScript Collective" == page_title.text

    authors = soup.select_one("article.tile p.title")
    assert "Margaret" == authors.text.strip()


def test_author_page(client_page: PageT) -> None:
    """The page for an author works."""
    soup = client_page("/authors/meg-1.html")
    page_title = soup.select_one("title")
    assert page_title and "Margaret | PyScript Collective" == page_title.text

    author = soup.select_one("main h1")
    assert "Margaret" == author.text.strip()
