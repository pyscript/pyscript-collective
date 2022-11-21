"""Provide a web server to browse the examples."""
import contextlib
from collections.abc import Iterator
from typing import AsyncContextManager

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse
from starlette.routing import Mount
from starlette.routing import Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.templating import _TemplateResponse

from psc.here import HERE
from psc.here import PYODIDE
from psc.here import PYSCRIPT
from psc.resources import Example
from psc.resources import Resources
from psc.resources import get_resources


templates = Jinja2Templates(directory=HERE / "templates")


async def favicon(request: Request) -> FileResponse:
    """Handle the favicon."""
    return FileResponse(HERE / "favicon.png")


async def homepage(request: Request) -> _TemplateResponse:
    """Handle the home page."""
    index_file = HERE / "index.html"
    root_path = "."

    return templates.TemplateResponse(
        "homepage.jinja2",
        dict(
            title="Home Page",
            main=index_file.read_text(),
            root_path=root_path,
            request=request,
        ),
    )


async def gallery(request: Request) -> _TemplateResponse:
    """Handle the gallery listing page."""
    resources = request.app.state.resources
    these_examples: Iterator[Example] = resources.examples.values()
    root_path = ".."
    these_authors = resources.authors

    return templates.TemplateResponse(
        "gallery.jinja2",
        dict(
            title="Gallery",
            examples=these_examples,
            root_path=root_path,
            request=request,
            authors=these_authors,
        ),
    )


async def authors(request: Request) -> _TemplateResponse:
    """Handle the author listing page."""
    these_authors: Iterator[Example] = request.app.state.resources.authors.values()
    root_path = "../.."

    return templates.TemplateResponse(
        "authors.jinja2",
        dict(
            title="Authors",
            authors=these_authors,
            root_path=root_path,
            request=request,
        ),
    )


async def author(request: Request) -> _TemplateResponse:
    """Handle an author page."""
    author_name = request.path_params["author_name"]
    resources: Resources = request.app.state.resources
    this_author = resources.authors[author_name]
    root_path = "../../.."

    return templates.TemplateResponse(
        "example.jinja2",
        dict(
            title=this_author.title,
            body=this_author.body,
            request=request,
            root_path=root_path,
        ),
    )


async def example(request: Request) -> _TemplateResponse:
    """Handle an example page."""
    example_name = request.path_params["example_name"]
    resources: Resources = request.app.state.resources
    this_example = resources.examples[example_name]
    root_path = "../../.."
    author_name = this_example.author
    if author_name:
        this_author = resources.authors.get(author_name, None)
    else:
        this_author = None

    # Set the pyscript URL to the CDN if we are being built from
    # the ``psc build`` command.
    user_agent = request.headers["user-agent"]
    if user_agent == "testclient":
        pyscript_url = "https://pyscript.net/latest/pyscript.js"
    else:
        pyscript_url = f"{root_path}/pyscript/pyscript.js"

    return templates.TemplateResponse(
        "example.jinja2",
        dict(
            title=this_example.title,
            subtitle=this_example.subtitle,
            extra_head=this_example.extra_head,
            body=this_example.body,
            request=request,
            root_path=root_path,
            pyscript_url=pyscript_url,
            author=this_author,
        ),
    )


async def example_code(request: Request) -> _TemplateResponse:
    """Handle the linked files for the code example."""
    example_name = request.path_params["example_name"]
    resources: Resources = request.app.state.resources
    this_example = resources.examples[example_name]
    root_path = "../../.."

    return templates.TemplateResponse(
        "example_code.jinja2",
        dict(
            title=f"{this_example.title} Code",
            extra_head=this_example.extra_head,
            request=request,
            root_path=root_path,
            linked_files=this_example.linked_files,
        ),
    )


async def content_page(request: Request) -> _TemplateResponse:
    """Handle a content page."""
    page_name = request.path_params["page_name"]
    resources: Resources = request.app.state.resources
    this_page = resources.pages[page_name]

    return templates.TemplateResponse(
        "page.jinja2",
        dict(
            title=this_page.title,
            subtitle=this_page.subtitle,
            body=this_page.body,
            request=request,
        ),
    )


routes = [
    Route("/", homepage),
    Route("/index.html", homepage),
    Route("/favicon.png", favicon),
    Route("/gallery/index.html", gallery),
    Route("/gallery", gallery),
    Route("/authors/index.html", authors),
    Route("/authors", authors),
    Route("/authors/{author_name}.html", author),
    Route("/gallery/examples/{example_name}/index.html", example),
    Route("/gallery/examples/{example_name}/code.html", example_code),
    Route("/gallery/examples/{example_name}/", example),
    Route("/pages/{page_name}.html", content_page),
    Mount("/gallery", StaticFiles(directory=HERE / "gallery")),
    Mount("/static", StaticFiles(directory=HERE / "static")),
]
if PYODIDE.exists():
    routes.append(Mount("/pyscript", StaticFiles(directory=PYSCRIPT)))
    routes.append(Mount("/pyodide", StaticFiles(directory=PYODIDE)))


@contextlib.asynccontextmanager  # type: ignore
async def lifespan(a: Starlette) -> AsyncContextManager:  # type: ignore
    """Run the resources factory at startup and make available to views."""
    a.state.resources = get_resources()
    yield


app = Starlette(
    debug=True,
    routes=routes,
    lifespan=lifespan,
)
