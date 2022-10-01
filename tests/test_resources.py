"""Construct the various kinds of resources: example, page, contributor."""
from pathlib import PurePath

import pytest
from bs4 import BeautifulSoup

from psc.here import HERE
from psc.resources import Example
from psc.resources import Page
from psc.resources import get_description
from psc.resources import get_head_nodes
from psc.resources import get_main_node_content
from psc.resources import get_pyscript_nodes
from psc.resources import get_resources
from psc.resources import tag_filter


@pytest.fixture
def head_soup() -> BeautifulSoup:
    """Get an example <head> with various nodes."""
    head = """
<link href="pyscript.css">
<link href="example.css">
<script src="pyscript.js"></script>
<script src="example.js"></script>
    """
    return BeautifulSoup(head, "html5lib")


def test_tag_filter(head_soup: BeautifulSoup) -> None:
    """Helper function to filter link and script from head."""
    excluded_link = head_soup.select("link")[0]
    assert not tag_filter(excluded_link, exclusions=("pyscript.css",))
    included_link = head_soup.select("link")[1]
    assert tag_filter(included_link, exclusions=("pyscript.css",))
    excluded_script = head_soup.select("script")[0]
    assert not tag_filter(excluded_script, exclusions=("pyscript.js",))
    included_script = head_soup.select("script")[1]
    assert tag_filter(included_script, exclusions=("pyscript.js",))


def test_description_not_present() -> None:
    """No index.md file in the example folder."""
    index_html_file = HERE / "examples/xx/index.html"
    html = get_description(index_html_file)
    assert html == ""


def test_description() -> None:
    """An index.md file is in the example folder."""
    index_html_file = HERE / "gallery/examples/hello_world/index.html"
    html = get_description(index_html_file)
    assert html == "<p>This is the <em>hello world</em> example.</p>\n"


def test_get_head_nodes(head_soup: BeautifulSoup) -> None:
    """Test the little helper for head nodes in the post init."""
    extra_head = get_head_nodes(head_soup)
    assert "example." in extra_head


def test_get_no_head_nodes() -> None:
    """The <head> has nothing interesting."""
    head = """
    <link href="pyscript.css">
    <script src="pyscript.js"></script>
        """
    head_soup = BeautifulSoup(head, "html5lib")
    extra_head = get_head_nodes(head_soup)
    assert extra_head == ""


def test_get_no_main() -> None:
    """Raise a ValueError if there is no main in an example."""
    example_html = "<body>Hello</body>"
    soup = BeautifulSoup(example_html, "html5lib")
    with pytest.raises(ValueError):
        get_main_node_content(soup)


def test_get_main() -> None:
    """Return the main node from an example."""
    example_html = '<body><main class="content">Hello <em>world</em></main></body>'
    soup = BeautifulSoup(example_html, "html5lib")
    main = get_main_node_content(soup)
    assert main == "Hello <em>world</em>"


def test_get_pyscript_nodes() -> None:
    """Run the helper to extract the stuff for pyscript."""
    example_html = """
<body>
  <py-config>X</py-config>
  <py-script>Y</py-config>
</body>
    """
    soup = BeautifulSoup(example_html, "html5lib")
    pyscript_nodes = get_pyscript_nodes(soup)
    assert "<py-config>" not in pyscript_nodes
    assert "<py-script>" in pyscript_nodes


def test_example_bad_path() -> None:
    """Point at an example that does not exist, get ValueError."""
    with pytest.raises(ValueError):
        Example(path=PurePath("XXXX"))


def test_example() -> None:
    """Construct an ``Example`` and ensure it has all the template bits."""
    this_example = Example(path=PurePath("hello_world"))
    assert this_example.title == "Hello World"
    assert (
        this_example.subtitle
        == "The classic hello world, but in Python -- in a browser!"
    )
    assert "hello_world.css" in this_example.extra_head
    assert "hello_world.js" in this_example.extra_head
    assert "<h1>Hello ...</h1>" in this_example.main
    assert "<py-config>" not in this_example.extra_pyscript
    assert "<py-script>" in this_example.extra_pyscript


def test_markdown_page() -> None:
    """Make an instance of a Page resource and test it."""
    this_page = Page(path=PurePath("about"))
    assert this_page.title == "About the PyScript Collective"
    assert "<h1>Helping" in this_page.body


def test_html_page() -> None:
    """Make an instance of a .html Page resource and test it."""
    this_page = Page(path=PurePath("contributing"))
    assert this_page.title == "Contributing"
    assert this_page.subtitle == "How to get involved in the PyCharm Collective."
    assert 'id="viewer"' in this_page.body


def test_page_optional_subtitle() -> None:
    """Frontmatter does not specify a subtitle."""
    this_page = Page(path=PurePath("contact"))
    assert this_page.title == "Contact Us"
    assert this_page.subtitle == ""


def test_missing_page() -> None:
    """Make a missing Page resource and test that it raises exception."""
    with pytest.raises(ValueError) as exc:
        Page(path=PurePath("xxx"))
    assert str(exc.value) == "No page at xxx"


def test_get_resources() -> None:
    """Ensure the dict-of-dicts is generated with PurePath keys."""
    resources = get_resources()

    # Example
    hello_world_path = PurePath("hello_world")
    hello_world = resources.examples[hello_world_path]
    assert hello_world.title == "Hello World"
    assert (
        hello_world.subtitle
        == "The classic hello world, but in Python -- in a browser!"
    )

    # Page
    about_path = PurePath("about")
    about = resources.pages[about_path]
    assert about.title == "About the PyScript Collective"
    assert "<h1>Helping" in about.body
