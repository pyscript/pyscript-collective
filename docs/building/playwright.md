# Playwright Interceptors

PyScript testing needs a real browser -- web components which load Pyodide and execute Python, then change the DOM.
[Playwright](https://playwright.dev/python/) provides this, but we'd like more convenience in the testing:

- Don't actually launch a web server to fetch the examples
- Make it easier to write examples and tests by having some automation

In this step we bring in Playwright, but don't yet use PyScript.
Here's the big idea: we do _not_ run a web server.
Instead, we write a Playwright interceptor as a pytest fixture.

## Install Playwright

We need to add Playwright to PSC.
In the current repo, this is done as part of a Makefile rule, which also copies the examples to a relative directory (bleh).

Instead, we'll just make it a development dependency.
If a Contributor wants to write an example, they just need to clone the repo and do a Poetry install with dev dependencies.
Kind of normal Python dev workflow.
To make it work in CI using Nox, we added this dependency to the `noxfile.py`.

This still requires running `playwright install` manually, to get the Playwright browsers globally installed.
That has to be added to PSC Contributor documentation.

## Fixture

With Playwright installed, now it is time to make it easier to write/run the tests for examples.
In the previous step, we did "shallow" testing of an example, using `TestClient` to ensure the HTML was returned.
We didn't actually load the HTML into a DOM, certainly didn't evaluate the PyScript web components, and _definitely_ didn't run some Python in Pyodide.

The current Collective uses Playwright's `page` fixture directly: you provide a URL, it tells the browser to make an HTTP request.
This means it needs an HTTP server running.
The repo fires up and shuts down a Python `SimpleHTTPServer` running in a thread, as part of test running.

If something gets hung...ouch.
You have to wait for the thread to time out.

PSC changes this by not running an HTTP server for testing the examples.
Instead, we use [Playwright interceptors](https://playwright.dev/python/docs/network#modify-responses).
When the URL comes in, our Python code runs and returns a response...quite like `TestClient` pretends to run an ASGI server.
Our "interceptor" looks at the URL, and if it is to the "fake" server, it reads/returns the path from disk.

This fixture is software, so we'll make a file at `src/psc/fixtures.py` and a test at `test_fixtures.py`.
We also need to make `tests/conftest.py` to load this as a pytest plugin.
The test file has dummy objects for the Playwright request/response/page/route etc.
The tests exercise the main code paths we need for the interceptor:

- A request but _not_ to the fake server URL should just be passed-through to an HTTP request
- A request to the fake server URL should extract the path
  - If that path exists in the project, read the file and return it
  - If not, raise a value error

With that in place, we write a `fixtures.fake_page` fixture function.
It asks `pytest` to inject the real `page`.
It then installs the interceptor by calling a helper function.
This helper function is what we actually write the fixture test for.

## Serve Up Examples

We aren't going to test by fetching examples from an HTTP server.
But our Viewers will look at examples from the HTTP server we made in the previous step.
Let's add that to `app.py` with another `Mount`, this time pointing `/examples` at `src/psc/examples`.
Also, add `first.html` with some dummy text as an "example".

Before the implementation, we add `test_app.test_first_example` as a failing test.
Then, once `app.py` is fixed, the test will pass.

## First Test

Our fixture is now in place, with a test that has good coverage.
We have a dummy example in `first.html`.
Let's write a test that uses Playwright and the interceptor.

We just added a `TestClient` test -- a kind of "shallow" test -- for `first.html`.
In `test_app.py` we add `test_first_example_full` as a Playwright test.

When we first run it, we see `fixture 'fake_page' not found`.
This is because `conftest.py` needs to load the `psc.fixtures`.
With that line added, the tests pass.

## Shallow vs. Full Markers

These Playwright tests are SLOW.
When we get a bunch of examples, it's going to be a pain.
As such, we'll want to emphasize unit tests and the shallow `TestClient` tests.

To make this first-class, we'll add 3 pytest markers to the project: unit, shallow, and full.
We do so in `pyproject.toml` along with the option to warn if someone uses an undefined customer marker.

With this in place, we add decorators such as `@pytest.mark.full` to our tests.
Later, we can run `pytest -m "not full"` to skip the Playwright tests.

## Better `TestClient` Testing

In this step we also improved the `TestClient` tests which makes sure our Starlette app serves what we expect.
Part of that means testing HTML, so we installed `beatifulsoup4` and made a fixture that lets us issue a request and get back `BeautifulSoup`.
These have rich CSS selector locators, so very convenient to use in tests.
This fixture also raise an exception if it doesn't get a `200` so you don't have to test that any more.

Just to be clear: `TestClient` tests are nice when you do *not* need to get into the JS/Pyodide side.
They are fast and zero mystery.

Of course, we added tests for those fixtures.

## QA

Cleaned up everything for pre-commit, mypy, nox, etc.
Coverage is still 100%.

Along the way, Typeguard got mad at the introduction of the marker.
I skipped investigation and just disabled Typeguard from the noxfile for now.
