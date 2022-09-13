"""The "models" for Example, Page, Contributor, etc.

We use paths as the "id" values. More specifically, PurePath.
"""
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from pathlib import PurePath
from typing import cast

from bs4 import BeautifulSoup
from bs4 import Tag
from markdown_it import MarkdownIt

from psc.here import HERE


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


def get_description(index_html_file: Path) -> str:
    """Read an index.md if present and convert to HTML."""
    md_file = index_html_file.parent / "index.md"
    if not md_file.exists():
        return ""
    md_content = md_file.read_text()
    md = MarkdownIt()
    return str(md.render(md_content))


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


def get_main_node_content(s: BeautifulSoup) -> str:
    """Get the main node but raise an exception if not present."""
    # Moving to a helper to allow testing ValueError without needing
    # to ship a broken (non-main) example.
    main_element = s.select_one("main")
    if main_element is None:  # pragma: no cover
        raise ValueError("Example file has no <main> element")
    return f"{main_element.decode_contents()}"


def get_pyscript_nodes(s: BeautifulSoup) -> str:
    """Find any pyscript nodes that are NOT ``py-config``."""
    pyscript_nodes = [
        pyscript.prettify()
        for pyscript in s.select("body > *")
        if pyscript and pyscript.name.startswith("py-") and pyscript.name != "py-config"
    ]
    return "\n".join(pyscript_nodes)


@dataclass
class Resource:
    """Base dataclass used for all resources."""

    path: PurePath
    title: str = ""
    main: str = ""
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
    extra_pyscript: str = ""
    subtitle: str = ""

    def __post_init__(self) -> None:
        """Extract most of the data from the HTML file."""
        index_html_file = HERE / "examples" / self.path / "index.html"
        if not index_html_file.exists():
            raise ValueError(f"No example at {self.path}")
        soup = BeautifulSoup(index_html_file.read_text(), "html5lib")

        # Title
        title_node = soup.select_one("title")
        self.title = title_node.text if title_node else ""

        # Subtitle
        subtitle_node = soup.select_one('meta[name="subtitle"]')
        assert subtitle_node  # noqa
        subtitle = cast(str, subtitle_node.get("content", ""))
        self.subtitle = subtitle

        # Description
        self.description = get_description(index_html_file)

        # Head
        self.extra_head = get_head_nodes(soup)

        # Main
        self.main = get_main_node_content(soup)

        # Extra PyScript
        self.extra_pyscript = get_pyscript_nodes(soup)


@dataclass
class Resources:
    """Container for all resources in site."""

    examples: dict[PurePath, Example] = field(default_factory=dict)


def get_resources() -> Resources:
    """Factory to construct all the resources in the site."""
    resources = Resources()

    # Load the examples
    examples_dir = HERE / "examples"
    examples = [e for e in examples_dir.iterdir() if e.is_dir()]
    for example in examples:
        this_path = PurePath(example.name)
        this_example = Example(path=this_path)
        resources.examples[this_path] = this_example
    return resources
