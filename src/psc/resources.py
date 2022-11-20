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
    pyscript_file = test_path / "pyscript.js"
    return pyscript_file.exists()


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

    name: str
    title: str = ""
    body: str = ""
    extra_head: str = ""


linked_file_mapping = dict(
    py="python",
    css="css",
    html="html"
)


@dataclass
class LinkedFile:
    """A source file on disk that gets attached to an example."""

    path: Path
    language: str = field(init=False)
    body: str = field(init=False)

    def __post_init__(self) -> None:
        """Read the file contents into the body."""
        self.language = linked_file_mapping[self.path.suffix[1:]]
        self.body = self.path.read_text()


@dataclass
class Example(Resource):
    """Create an example from an HTML location on disk.

    We will use a PurePath as a key. It isn't meant to point to an
    actual file on disk. Instead, it will be like ``hello_world``. When
    we go to actually open the file, we'll add the "policy part".
    Meaning, HERE / "examples" / name / "index.html".
    """

    subtitle: str = field(init=False)
    description: str = field(init=False)
    author: str = field(init=False)
    linked_files: list[LinkedFile] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Extract most of the data from the HTML file."""
        # Title, subtitle, body come from the example's MD file.
        index_md_file = HERE / "gallery/examples" / self.name / "index.md"
        md_fm = frontmatter.load(index_md_file)
        self.title = md_fm.get("title", "")
        self.author = md_fm.get("author", "")
        self.subtitle = md_fm.get("subtitle", "")
        md = MarkdownIt()
        self.description = str(md.render(md_fm.content))

        # Main, extra head example's HTML file.
        this_example_path = HERE / "gallery/examples" / self.name
        index_html_file = this_example_path / "index.html"
        if not index_html_file.exists():  # pragma: nocover
            raise ValueError(f"No example at {self.name}")
        index_html_text = index_html_file.read_text()
        soup = BeautifulSoup(index_html_text, "html5lib")
        self.extra_head = get_head_nodes(soup)
        self.body = get_body_content(soup)

        # Process any linked files
        linked_paths = [*["index.html"], *md_fm.get("linked_files", [])]
        for linked_name in linked_paths:
            linked_path = this_example_path / linked_name
            linked_file = LinkedFile(path=linked_path)
            self.linked_files.append(linked_file)


@dataclass
class Author(Resource):
    """Information about an author, from Markdown."""

    def __post_init__(self) -> None:
        """Initialize the rest of the fields from the Markdown."""
        md_file = HERE / "gallery/authors" / f"{self.name}.md"
        md_fm = frontmatter.load(md_file)
        self.title = md_fm.get("title", "")
        md = MarkdownIt()
        self.body = str(md.render(md_fm.content))


@dataclass
class Page(Resource):
    """A Markdown+frontmatter driven content page."""

    subtitle: str = ""

    def __post_init__(self) -> None:
        """Extract content from either Markdown or HTML file."""
        md_file = HERE / "pages" / f"{self.name}.md"
        html_file = HERE / "pages" / f"{self.name}.html"

        # If this self.name resolves to a Markdown file, use it first
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
            raise ValueError(f"No page at {self.name}")


@dataclass
class Resources:
    """Container for all resources in site."""

    authors: dict[str, Author] = field(default_factory=dict)
    examples: dict[str, Example] = field(default_factory=dict)
    pages: dict[str, Page] = field(default_factory=dict)


def get_sorted_paths(target_dir: Path, only_dirs: bool = True) -> list[PurePath]:
    """Return an alphabetized listing of the examples."""
    if only_dirs:
        paths = [e for e in target_dir.iterdir() if e.is_dir()]
    else:
        paths = [e for e in target_dir.iterdir()]

    return sorted(paths, key=attrgetter("name"))


def get_resources() -> Resources:
    """Factory to construct all the resources in the site."""
    resources = Resources()

    # Load the authors
    authors = HERE / "gallery/authors"
    for author in get_sorted_paths(authors, only_dirs=False):
        this_author = Author(name=author.stem)
        resources.authors[author.stem] = this_author

    # Load the examples
    examples = HERE / "gallery/examples"
    for example in get_sorted_paths(examples):
        this_example = Example(example.stem)
        resources.examples[example.stem] = this_example

    # Load the Pages
    pages_dir = HERE / "pages"
    pages = [e for e in pages_dir.iterdir()]
    for page in pages:
        this_page = Page(name=page.stem)
        resources.pages[page.stem] = this_page

    return resources
