"""Provide a web server to browse the examples."""
from pathlib import Path

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse
from starlette.routing import Mount
from starlette.routing import Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.templating import _TemplateResponse

from psc.here import PYODIDE
from psc.here import PYSCRIPT
from psc.here import STATIC


HERE = Path(__file__).parent
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


routes = [
    Route("/", homepage),
    Route("/index.html", homepage),
    Route("/favicon.png", favicon),
    Mount("/examples", StaticFiles(directory=HERE / "examples")),
    Mount("/static", StaticFiles(directory=STATIC)),
    Mount("/pyscript", StaticFiles(directory=PYSCRIPT)),
    Mount("/pyodide", StaticFiles(directory=PYODIDE)),
]

app = Starlette(debug=True, routes=routes)
