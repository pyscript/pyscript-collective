"""Test cases for the __main__ module."""
import pytest
from typer.testing import CliRunner

from psc.__main__ import app


runner = CliRunner()

#
# @pytest.mark.full
# def test_download() -> None:
#     """Run the Pyodide/PyScript downloader."""
#     result = runner.invoke(app, ["download", "--dry-run"])
#     assert result.exit_code == 0
#     assert "Downloaded Pyodide" not in result.stdout
#     assert "Downloaded PyScript" not in result.stdout


def test_build() -> None:
    """Run the site builder."""
    result = runner.invoke(app, ["build"])
    assert result.exit_code == 0
    assert "Building to the public directory" in result.stdout


def test_start() -> None:
    """Ensure the examples home page works as expected."""
    result = runner.invoke(app, ["start", "--dry-run"])
    assert result.exit_code == 0
    assert "Skipping server startup" in result.stdout
