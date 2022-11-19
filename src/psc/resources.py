"""The "models" for Example, Page, Contributor, etc.

We use paths as the "id" values. More specifically, PurePath.
"""
from dataclasses import dataclass
from dataclasses import field
from operator import attrgetter
from pathlib import Path
from pathlib import PurePath
from typing import cast

import frontmatter
from bs4 import BeautifulSoup
from bs4 import Tag
from markdown_it import MarkdownIt

from psc.here import HERE
from psc.here import PYODIDE

EXCLUSIONS = ("pyscript.css", "pyscript.js", "favicon.png")


def tag_filter(
        tag: Tag,
        exclusions: tuple[str, ...] = EXCLUSIONS,
) -> bool:
    """Filter nodes from example that should not get included."""
    attr = "href" if tag.name == "link" else "src"
    # We have to do the cast because BeautifulSoup can return a
    # list of values if the HTML does something special.
    # https://beautiful-soup-4.readthedocs.io/en/latest/index.html#multi-valued-attributes
    attr_value = cast(str, tag.get(attr))
    for exclusion in exclusions:
        if attr_value.endswith(exclusion):
            return False
    return True


def get_head_nodes(s: BeautifulSoup) -> str:
    """Make post init simpler by putting head node helper here."""
    head_nodes = [
        node.prettify()
        for node in s.select("head > link, head > script")
        if tag_filter(node)
    ]
    if head_nodes:
        return "\n".join(head_nodes)
    return ""


def is_local(test_path: Path = PYODIDE) -> bool:
    """Use a policy to decide local vs. CDN mode."""
    return test_path.exists()


def get_body_content(s: BeautifulSoup, test_path: Path = PYODIDE) -> str:
    """Get the body node but raise an exception if not present."""
    # Choose the correct TOML file for local vs remote.
    toml_name = "local" if is_local(test_path) else "cdn"
    src = f"../py_config.{toml_name}.toml"

    # Get the body and patch the py_config src
    body_element = s.select_one("body")
    if body_element:
        py_config = body_element.select_one("py-config")
        if py_config:
            py_config.attrs["src"] = src
            return f"{body_element.decode_contents()}"
    return ""


@dataclass
class Resource:
    """Base dataclass used for all resources."""

    path: PurePath
    title: str = ""
    body: str = ""
    extra_head: str = ""


@dataclass
class Example(Resource):
    """Create an example from an HTML location on disk.

    We will use a PurePath as a key. It isn't meant to point to an
    actual file on disk. Instead, it will be like ``hello_world``. When
    we go to actually open the file, we'll add the "policy part".
    Meaning, HERE / "examples" / name / "index.html".
    """

    description: str = ""
    subtitle: str = ""

    def __post_init__(self) -> None:
        """Extract most of the data from the HTML file."""
        # Title, subtitle, description come from the example's MD file.
        index_md_file = HERE / "gallery/examples" / self.path / "index.md"
        md_fm = frontmatter.load(index_md_file)
        self.title = md_fm.get("title", "")
        self.subtitle = md_fm.get("subtitle", "")
        md = MarkdownIt()
        self.description = str(md.render(md_fm.content))

        # Main, extra head example's HTML file.
        index_html_file = HERE / "gallery/examples" / self.path / "index.html"
        if not index_html_file.exists():  # pragma: nocover
            raise ValueError(f"No example at {self.path}")
        soup = BeautifulSoup(index_html_file.read_text(), "html5lib")
        self.extra_head = get_head_nodes(soup)
        self.body = get_body_content(soup)


@dataclass
class Page(Resource):
    """A Markdown+frontmatter driven content page."""

    subtitle: str = ""
    body: str = ""

    def __post_init__(self) -> None:
        """Extract content from either Markdown or HTML file."""
        md_file = HERE / "pages" / f"{self.path}.md"
        html_file = HERE / "pages" / f"{self.path}.html"

        # If this self.path resolves to a Markdown file, use it first
        if md_file.exists():
            md_fm = frontmatter.load(md_file)
            self.title = md_fm.get("title", "")
            self.subtitle = md_fm.get("subtitle", "")
            md = MarkdownIt()
            self.body = str(md.render(md_fm.content))
        elif html_file.exists():
            soup = BeautifulSoup(html_file.read_text(), "html5lib")
            title_node = soup.find("title")
            if title_node:
                self.title = title_node.text
            subtitle_node = soup.select_one('meta[name="subtitle"]')
            if subtitle_node:
                assert subtitle_node  # noqa
                subtitle = cast(str, subtitle_node.get("content", ""))
                self.subtitle = subtitle
            body_node = soup.find("body")
            if body_node and isinstance(body_node, Tag):
                self.body = body_node.prettify()
        else:  # pragma: no cover
            raise ValueError(f"No page at {self.path}")


@dataclass
class Resources:
    """Container for all resources in site."""

    examples: dict[PurePath, Example] = field(default_factory=dict)
    pages: dict[PurePath, Page] = field(default_factory=dict)


def get_sorted_examples() -> list[PurePath]:
    """Return an alphabetized listing of the examples."""
    examples_dir = HERE / "gallery/examples"
    examples = [e for e in examples_dir.iterdir() if e.is_dir()]
    return sorted(examples, key=attrgetter("name"))


def get_resources() -> Resources:
    """Factory to construct all the resources in the site."""
    resources = Resources()

    # Load the examples
    for example in get_sorted_examples():
        this_path = PurePath(example.name)
        this_example = Example(path=this_path)
        resources.examples[this_path] = this_example

    # Load the Pages
    pages_dir = HERE / "pages"
    pages = [e for e in pages_dir.iterdir()]
    for page in pages:
        this_path = PurePath(page.stem)
        this_page = Page(path=this_path)
        resources.pages[this_path] = this_page

    return resources
