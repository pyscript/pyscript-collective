"""Test cases for the __main__ module."""
from typer.testing import CliRunner

from psc.__main__ import app


runner = CliRunner()


def test_main() -> None:
    """Ensure the examples home page works as expected."""
    result = runner.invoke(app, ["--dry-run"])
    assert result.exit_code == 0
    assert "Skipping server startup" in result.stdout
