"""Provide a web server to browse the examples."""
import contextlib
from pathlib import PurePath
from typing import AsyncContextManager
from typing import Iterator

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

    return templates.TemplateResponse(
        "page.jinja2",
        dict(
            title="Home Page",
            main=index_file.read_text(),
            request=request,
        ),
    )


async def examples(request: Request) -> _TemplateResponse:
    """Handle the examples listing page."""
    these_examples: Iterator[Example] = request.app.state.resources.examples.values()

    return templates.TemplateResponse(
        "examples.jinja2",
        dict(
            title="Examples",
            examples=these_examples,
            request=request,
        ),
    )


async def example(request: Request) -> _TemplateResponse:
    """Handle an example page."""
    example_path = PurePath(request.path_params["example_name"])
    resources: Resources = request.app.state.resources
    this_example = resources.examples[example_path]

    return templates.TemplateResponse(
        "example.jinja2",
        dict(
            title=this_example.title,
            subtitle=this_example.subtitle,
            extra_head=this_example.extra_head,
            main=this_example.main,
            extra_pyscript=this_example.extra_pyscript,
            request=request,
        ),
    )


routes = [
    Route("/", homepage),
    Route("/index.html", homepage),
    Route("/favicon.png", favicon),
    Route("/examples/index.html", examples),
    Route("/examples", examples),
    Route("/examples/{example_name}/index.html", example),
    Route("/examples/{example_name}/", example),
    Mount("/examples", StaticFiles(directory=HERE / "examples")),
    Mount("/static", StaticFiles(directory=HERE / "static")),
    Mount("/pyscript", StaticFiles(directory=PYSCRIPT)),
    Mount("/pyodide", StaticFiles(directory=PYODIDE)),
]


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
