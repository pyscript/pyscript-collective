"""Command-line interface for PSC."""
import os
import tarfile
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory

import typer
import uvicorn
from starlette.testclient import TestClient
from urllib3 import HTTPResponse
from urllib3 import PoolManager

from psc.here import HERE
from psc.resources import get_resources


app = typer.Typer()


def rmtree(root: Path) -> None:
    """Recursively remove everything in the target path."""
    for p in root.iterdir():
        if p.is_dir():
            rmtree(p)
        else:
            p.unlink()

    root.rmdir()


@app.command()
def download(
    dry_run: bool = typer.Option(False, "--dry-run")
) -> None:  # pragma: no cover
    """Download Pyodide and PyScript distributions into project dir."""
    http = PoolManager()

    # Get Pyodide first
    pyodide_url_prefix = "https://github.com/pyodide/pyodide/releases/download"
    pyodide_url = f"{pyodide_url_prefix}/0.21.3/pyodide-build-0.21.3.tar.bz2"
    pyodide_request: HTTPResponse = http.request("GET", pyodide_url)  # type: ignore
    with TemporaryDirectory() as tmp_dir_name:
        os.chdir(tmp_dir_name)
        tmp_dir = Path(tmp_dir_name)
        temp_file = tmp_dir / "pyodide.tar.bz2"
        temp_file.write_bytes(pyodide_request.data)
        tar = tarfile.open(temp_file)
        tar.extractall()
        target = HERE / "pyodide"
        if not dry_run:
            copytree(tmp_dir / "pyodide", target, dirs_exist_ok=True)
            print("Downloaded Pyodide")

    # Next, PyScript
    filenames = ("pyscript.js", "pyscript.js.map")
    for fn in filenames:
        pyscript_url = f"https://pyscript.net/latest/{fn}"
        pyscript_request: HTTPResponse = http.request(
            "GET", pyscript_url
        )  # type: ignore
        if not dry_run:
            target = HERE / "pyscript"
            if not dry_run:
                with open(target / fn, "wb") as pyscript_output:
                    pyscript_output.write(pyscript_request.data)

            print("Downloaded PyScript")


@app.command()
def build() -> None:  # pragma: no cover
    """Write the export to a public directory."""
    print("Building to the public directory")

    # If the target directory exists, remove it, then copy everything
    # under src/psc to the target
    public = HERE.parent.parent / "dist/public"
    if public.exists():
        rmtree(public)
    copytree(HERE, public)

    # Setup test client async with our app
    from psc.app import app as web_app

    with TestClient(web_app) as test_client:
        # Render the home page then write to the output directory
        response = test_client.get("/")
        assert response.status_code == 200
        html = response.text
        output = public / "index.html"
        output.write_text(html)

        # Same for gallery page
        response = test_client.get("/gallery/index.html")
        assert response.status_code == 200
        html = response.text
        # output = public / "gallery/index.html"
        with open(public / "gallery/index.html", "w") as f:
            f.write(html)

        # Now for each page
        resources = get_resources()
        for page in resources.pages.values():
            response = test_client.get(f"/pages/{page.path.stem}.html")
            output = public / f"pages/{page.path.stem}.html"
            output.write_text(response.text)

        # And for each example
        for example in resources.examples.values():
            url = f"/gallery/examples/{example.path.stem}/index.html"
            response = test_client.get(url)
            output = public / f"gallery/examples/{example.path.stem}/index.html"
            output.write_text(response.text)


# @app.callback(invoke_without_command=True)
@app.command()
def start(dry_run: bool = typer.Option(False, "--dry-run")) -> None:  # pragma: no cover
    """Default command, used to start the server."""
    # If running from the test, we don't want to actually start server
    if dry_run:
        print("Skipping server startup")
    else:
        print("Starting server")
        uvicorn.run("psc:app", port=3000, log_level="info")  # pragma: no cover
