"""Terribly simple test suite for terribly simple function."""
from psc.here import HERE


def test_here() -> None:
    """Ensure we have the correct top-of-the-package."""
    assert HERE.name == "psc"
