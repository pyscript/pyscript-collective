# CDN Mode

Add a way to get PyScript/Pyodide locally sometimes, but from CDN other times.

## Why

When running and testing locally, the developers (and example writers) want fast turnaround.
They don't want to keep going out on a possibly-slow network -- or even no-network, if offline.
In "production", though, we want people browsing the examples to get the CDN version.

Other times are harder to decide.
GitHub Actions would like a nice speedup.
But it will take some investigation to learn how to cache artifacts.

## When

There are several contexts where this decision needs to be made.

## Standalone Example

The Gallery examples are designed to allow people to preview an example's `index.html` without the app.
They have a `<script>` in `<head>` pointed at `pyscript.js`.
They also have a `<py-config>` in the body to point at a Pyodide runtime.

We encourage them to point at the locally-downloaded assets.
The build step then removes those nodes from the generated output, inserting the Gallery's decision on both.

### Local Web App

Some people will pip install the PSC and go through them locally.
Perhaps even hack on them.
Or, contributors writing an example will want a preview.
Both will fire up Starlette locally.

### Local Playwright

When running an "end-to-end" (E2E) test, you want fast turnaround.
You don't want to go out on the network, repeatedly.

### Local/GHA Nox

Nox is used to run our "machinery" in isolation.
We run it locally, as a last step before pushing.
We might also run it locally just for automation, e.g. the reloading Sphinx server.
But it also runs when GitHub Actions workflows call it.

In theory, you want local Nox to be exactly the same as GHA Nox.
Otherwise, you aren't recreating the build environment.

### Production Static Website

The GHA generates a static website.
This should be pointed at the CDN

## Where

The moral of the story: we should point at the CDN *unless* something says to point at local.
There are several places we make point at assets.

### `pyscript.js`

Two locations.
First, in an example's `index.html`, when it is viewed "standalone".
Second, in the `example.jinja2` template's `<head>`.

### `gallery/examples/pyconfig.toml`

This is also pointed to in two locations.
Again, from an example's `index.html`.
Here you'll have a `<py-config src="../pyconfig.toml">` node which might include some instructions in the content.

## Solution

During local (non-CDN) use, we'll change the `<py-config>` to use `src="pyconfig.local.toml`.

How?
We're already using BeautifulSoup to pick apart the `index.html`.
Once we make the local vs. CDN decision, we can easily change the `src` attribute to point either TOML file.

What is the local vs. CDN criteria?
We'll just look for the `src/pyscript` and `src/pyodide` directory.
If they exist, then someone downloaded the assets.
That's a good flag for whether to point at those directories.

What is the action to take?
The `py_config.local.toml` file has a `runtimes.src` entry pointing to the local `pyodide.js`.
The `py_config.cdn.toml` file points at the CDN version.

## Actions

- Remove the timeout
- Test/implementation that calls a `is_local` function to detect the correct mode
- Test/implementation which wires that into the HTML munger
