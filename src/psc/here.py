"""Paths that can be referenced anywhere and get the right target."""
from pathlib import Path

HERE = Path(__file__).parent
STATIC = HERE / "static"
PYODIDE = HERE / "pyodide"
PYSCRIPT = HERE / "pyscript"
