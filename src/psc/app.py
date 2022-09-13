"""Provide a web server to browse the examples."""
from http.client import HTTPException
from pathlib import Path

from bs4 import BeautifulSoup
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


async def example(request: Request) -> _TemplateResponse:
    """Handle an example page."""
    example_name = request.path_params["example_name"]
    example_file = HERE / "examples" / example_name / "index.html"
    example_content = example_file.read_text()
    soup = BeautifulSoup(example_content, "html5lib")

    # Get the example title from the HTML file
    title_node = soup.select_one("title")
    title = title_node.text if title_node else ""

    # Assemble any extra head
    extra_head_links = [
        link.prettify()
        for link in soup.select("head link")
        if not link.attrs["href"].endswith("pyscript.css")
        and not link.attrs["href"].endswith("favicon.png")
    ]
    extra_head_scripts = [
        script.prettify()
        for script in soup.select("head script")
        if not script.attrs["src"].endswith("pyscript.js")
    ]
    extra_head_nodes = extra_head_links + extra_head_scripts
    extra_head = "\n".join(extra_head_nodes)

    # Assemble the main element
    main_element = soup.select_one("main")
    if main_element is None:
        raise HTTPException("Example file has no <main> element")
    main = f"<main>{main_element.decode_contents()}</main>"

    # Get any non-py-config PyScript nodes
    pyscript_nodes = [
        pyscript.prettify()
        for pyscript in soup.select("body > *")
        if pyscript.name.startswith("py-") and pyscript.name != "py-config"
    ]
    extra_pyscript = "\n".join(pyscript_nodes)

    return templates.TemplateResponse(
        "example.jinja2",
        dict(
            title=title,
            extra_head=extra_head,
            main=main,
            extra_pyscript=extra_pyscript,
            request=request,
        ),
    )


routes = [
    Route("/", homepage),
    Route("/index.html", homepage),
    Route("/favicon.png", favicon),
    Route("/examples/{example_name}/index.html", example),
    Mount("/examples", StaticFiles(directory=HERE / "examples")),
    Mount("/static", StaticFiles(directory=STATIC)),
    Mount("/pyscript", StaticFiles(directory=PYSCRIPT)),
    Mount("/pyodide", StaticFiles(directory=PYODIDE)),
]

app = Starlette(debug=True, routes=routes)
