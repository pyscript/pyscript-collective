# Command Runner

We want to make it easy for Viewers to see the examples locally.
In fact, to easily tinker with them and see changes.

Let's add a CLI that fires up a Starlette/uvicorn web server.

## CLI

I'll use [Typer](http://typer.tiangolo.com) to manage the CLI, with `typer[all]` as the installation to get Rich.
I then add a single entry point in `__main__.py` and ensure it is registered in `pyproject.toml`.
I then add a test in `tests/test_main.py` to ensure it works as expected.

This was a little tricky.
I don't want to actually run the server in the CLI and Typer spawns a subprocess, so I can't mock (I think?)
Thus, I added a CLI option I could pass in to prevent the server from starting.

With this, users can run, in their virtualenv once PSC is installed:

```bash
$ python -m psc
```

If you have `pipx` installed (and if PSC were actuall uploaded to PyPI):

```bash
$ pipx psc
```

I can run in my editable-install:

```bash
$ poetry run python -m psc
```

## Web App

I'll use Starlette and uvicorn.
In this step, it's just one route which returns static HTML, plus a static directory hosting a single CSS file.
Of course, this starts with `test_app.py`.

I can test this easily using `TestClient` which requires an installation of `requests`.

:::{note} Nice way to run tests
`TestClient` is nice because it doesn't start an actual server.
That's a big part of the complaint on the current testing strategy for PyScript.
The `SimpleHTTPServer` running in a thread is kind of fragile for getting hung.
:::

## Wrapup

As cleanup, we'll delete the pre-existing `exampls/hello_world.html` and `tests/test_examples.py`.
They'll make a re-appearance.

In the previous step we neglected to replace the existing Collective `.github/workflows` file with the workflows from Hypermodern.
We did so in this step.

I run pre-commit, mypy, and nox.
Everything is good, onward.
