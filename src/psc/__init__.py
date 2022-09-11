"""PyScript Collective."""

from pathlib import Path


# Paths that can be referenced anywhere and get the right target.

SRC = Path(__file__).parent
STATIC = SRC / "static"
