# Proper Package

This PSC isn't just prototyping examples to list on a webpage.
It's actually an installable Python package, making it easy for people to _consume and tinker with_ the examples.

As such, PSC starts with a clean-slate:

- Updated from (controversially) the [Hypermodern Python cookiecutter](https://cookiecutter-hypermodern-python.readthedocs.io/en/latest/index.html)
- An installable package on PyPI
- A full Collective documentation site based on Sphinx

Let's look at each decision in detail.

## Hypermodern Cookiecutter

This effort builds the Collective atop a Hypermodern cookiecutter package.
Meaning: Poetry, pytest, pre-commit, mypy, nox, GitHub actions, Sphinx, and other Python tooling.

Admittedly, this is an *aggressive* decision.
The reasoning:

- We want the Collective to be good examples of Python coding
- Extra work to make them easy to learn
- Since the Collective will assume the maintenance, extra work on tests, quality, and standards.

We acknowledge that this raises the bar for contribution.
(We can turn off some knobs to be less strict.)
It is likely that we do the work to convert a PR into a passing contribution.

## Installable Package

As part of the Collective reboot, it's written as if it is a Python package, meant to be installed.
This will potentially make it dead-simple for people to play with the examples, even to edit them and see results.
They will just `pip install our-package` and get everything needed.
Or even simpler, use `pipx` to just run the examples.

:::{attention} Package name?
The PyScript ecosystem should adopt a prefix for add-on packages, as done in Django, Flask, Pyramid, etc.
Presumably this package will be named `pyscript-collective`.

That's pretty long, though.
Perhaps PyScript should adopt `ps-` as the prefix?
With the Collective adopting `psc-` for a prefix?
:::

## Conda -> Poetry

The existing `pyscript-collective` repo starts with a `Makefile`.
It also presumes Conda for everything.

This effort switches over to Poetry for contributors and pip for consumers.
The use of Poetry isn't important -- we could easily switch to `virtualenv` and `requirements.txt`.
But the switch away from Conda is more intentional: it's less used per the PSF survey, and we want to show that PyScript isn't tied to Anaconda nor Conda.

## Docs in Sphinx

This Collective repo will need documentation for contributors, maintainers and others.

:::{note} Docs, not website
Just to be clear, this section describes the *docs* for the Collective, not the *website* and web app that are ultimately created.
:::

The Hypermodern Sphinx setup does an include of Markdown files stored in the repo root: README, Code of Conduct, license, etc.
Those needed some fixing to be MyST compliant.
For example, we edited the Sphinx `conf.py` file to enable MyST [autogenerate headers](https://myst-parser.readthedocs.io/en/v0.17.1/syntax/optional.html#syntax-header-anchors) to make the README internal links happy.

We also copied over the Code of Conduct text from the PyScript repo.
