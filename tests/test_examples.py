"""Run tests on each PyScript Collective example."""

from psc import hello


def test_hello() -> None:
    """Fake test."""
    assert hello() == "World"
