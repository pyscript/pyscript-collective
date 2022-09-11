"""Sphinx configuration."""
project = "PyScript Collective"
author = "PyScript Collective"
copyright = "2022, PyScript"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
myst_heading_anchors = 4
