"""Command-line interface for PSC."""

import typer
import uvicorn


app = typer.Typer()


@app.command()
def main(dry_run: bool = typer.Option(False, "--dry-run")) -> None:  # pragma: no cover
    """Default command, used to start the server."""
    # If running from the test, we don't want to actually start server
    if dry_run:
        print("Skipping server startup")
    else:
        print("Starting server")
        uvicorn.run("psc:app", port=3000, log_level="info")  # pragma: no cover


if __name__ == "__main__":  # pragma: no cover
    app()
