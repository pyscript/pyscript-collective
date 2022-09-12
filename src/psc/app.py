"""Provide a web server to browse the examples."""

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse
from starlette.responses import HTMLResponse
from starlette.routing import Mount
from starlette.routing import Route
from starlette.staticfiles import StaticFiles

from .here import HERE, PYSCRIPT
from .here import PYODIDE
from .here import STATIC


async def favicon(request: Request) -> FileResponse:
    """Route just for serving the favicon."""
    return FileResponse(HERE / "favicon.png")


def index_page(request: Request) -> HTMLResponse:
    """Handle the home page."""
    return HTMLResponse("<h1>Hello, world!</h1>")


routes = [
    Route("/", index_page),
    Mount("/static", StaticFiles(directory=STATIC)),
    Route("/favicon.png", favicon),
    Mount("/examples", StaticFiles(directory=HERE / "examples")),
    Mount("/pyscript", StaticFiles(directory=PYSCRIPT)),
    Mount("/pyodide", StaticFiles(directory=PYODIDE)),
]

app = Starlette(debug=True, routes=routes)
