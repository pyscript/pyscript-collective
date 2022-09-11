"""Provide a web server to browse the examples."""

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.routing import Mount
from starlette.routing import Route
from starlette.staticfiles import StaticFiles

from . import STATIC


def index_page(request: Request) -> HTMLResponse:
    """Handle the home page."""
    return HTMLResponse("<h1>Hello, world!</h1>")


routes = [
    Route("/", index_page),
    Mount("/static", StaticFiles(directory=STATIC)),
]

app = Starlette(debug=True, routes=routes)
