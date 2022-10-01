# First PyScript Example

Well, that was certainly a lot of prep.

Let's get into PyScript and examples.
In this step we'll add the "Hello World" example along with unit/shallow/full tests.
We will _not_ though go further into how this example gets listed.
We also won't do any automation across examples: each example gets its own tests.

Big ideas: tests run offline and faster, no quirks for threaded server, much simpler "wait" for DOM.

## Re-Organize Tests

In the previous step, we made an `src/psc/examples` directory with `first.html` in it.
Let's remove `first.html` and instead, have a `hello_world` directory with `index.html` in it.
For now, it will be the same content as `first.html`, though we need to change the CSS path to `../static/psc.css`.

We also have our "first example" tests in `test_app.py`.
Let's leave that test file to test the application itself, not each individual test.
Thus, let's start `tests/examples/test_hello_world.py` and move `test_first_example*` into it.
We'll finish with `test_hello_world` and `test_hello_world_full` in that file.

With these changes, the tests pass.
Let's change the example to be the actual PyScript `Hello World` HTML file.

## Download PyScript/Pyodide Into Own Directories

Using `curl`, I grabbed the latest `pyscript.js`  plus the `.map` etc.
I did NOT check these into the repo.
Instead, I made a `src/pyscript` directory, which also meant making a route, which also meant making a test.

This brings up an interesting question about versions.
Should the Collective examples all use the same PyScript/Pyodide versions, or do we need to support variations?

Next up, Pyodide.
I got the `.bz2` from the releases and uncompressed/untarred into a release directory.
Bit by bit, I copied over pieces until "Hello World" loaded:

- The `.mjs` and `.asm*`
- `packages.json`
- The distutils.tar and pyodide_py.tar files
- `.whl` directories for micropip, packaging, and pyparsing

Later we'll provide a command-line step to automate this (and to handle it for CI.)

## Hello World Example

Back to `src/psc/examples/hello_world/index.html`.
Before starting, we should ensure the shallow test -- `TestClient` -- in `test_hello_world.py` works.

To set up PyScript, first, in `head`:

```html
<link rel="icon" type="image/png" href="../../favicon.png" />
<script defer src="../../static/pyscript.js"></script>
```

That gets PyScript stuff.

To get Pyodide from a local installation instead of the network, I added `<py-config>`:

```xml
<py-config>
- autoclose_loader: true
  runtimes:
    - src: "../../pyodide/pyodide.js"
      name: pyodide-0.20
      lang: python
</py-config>
```

This was complicated by a few factors:

- The [PyScript docs page is broken](https://github.com/pyscript/pyscript/issues/528)
- There are no examples in PyScript (and thus no tests) that show a working version of `<py-config>`
- The default value on `autoclose_loader` appears to be `false` so if you use `<py-config>` you need to explicitly turn it off.
- If you reformat your code, the YAML gets mis-formatted and it is a pain to debug
- We want the path to `pyodide.js` to work if you load the `index.html` directly or through a server

At this point, the page loaded correctly in a browser, going to `http://127.0.0.1:3000/examples/hello_world/index.html`.
Now, on to Playwright.

## Playwright Interceptor

We're going to be handling more types of files now, so we change the `Content-Type` sniffing.
Instead of looking at the extension, we use Python's `mimetypes` library.

For the test, we want to check that our PyScript output is written into the DOM.
This doesn't happen immediately.
In the PyScript repo, they sniff at console messages and do a backoff to wait for Pyodide execution.

Playwright has help for this.
The `page` can [wait for a selector to be satisfied](https://playwright.dev/python/docs/api/class-page#page-wait-for-selector).

This is _so much nicer_.
Tests run a LOT faster:

- Our assets (HTML, CSS, `pyscript.js`, `pyscript.css`) are served without an HTTP server
- Pyodide itself isn't loaded from CDN nor even HTTP
  Also, if something goes wrong, you aren't stuck with a hung thread in `SimpleHTTPServer`.
  Finally, as I noticed when working on vacation with terrible Internet -- everything can run offline...the examples and their tests.

It was _very_ hard to get to this point, as I ran into a number of obscure bugs:

- The `<py-config>` YAML bug above was a multi-hour waste
- Reading files as strings failed obscurely on Pyodide's `.asm.*` files
- Ditto for MIME type, which needs to be `application/wasm` (though the interwebs are confusing on this)
- Any time the flake8/black/prettier stack ran on stuff in static, all hell broke loose

## Debugging

It was kind of miserable getting to this point.
What debugging techniques did I discover?

Foremost, running the Playwright test in "head-ful" mode and looking at both the Chromium console and the network tab.
Playwright made it easy, including with the little controller UI app that launches and lets you step through:

```bash
$ PWDEBUG=1 poetry run pytest -s tests/examples/test_hello_world.py
```

For this, it can help to add a `page.pause()` after the `page.goto()`.
Otherwise, use the Playwright controls in the popup window to step through the execution.

Next, when running like this, you can use Python `print()` statements that write to the console which launched the head-ful client.
That's useful in the interceptor.
You could alternatively do some console logging with Playwright's (cumbersome) syntax for talking to the page from Python.
But diving into the Chromium console is a chore.

When things weren't in "fail catastrophically" mode, the most productive debugging was...in the debugger.
I set a breakpoint interceptor code, ran the tests, and stopped on each "file" request.

Finally, the most important technique was to...slow down and work methodically with unit tests.
I should have done this from the start, hardening the interceptor and its surface area with Playwright.
I spent hours on things a decent test (and even `mypy`) would have told me about bytes vs. strings.

## QA Tools

When running `pre-commit`, it appears Prettier re-formats the YAML contents of `<py-config>`.
I could have spent time to figure it out (e.g. skip those files, or teach Prettier how to handle it.)
But it's not urgent, so I disabled Prettier in the `.pre-commit-config.yaml` file.

Flake8 had a lot of complaints with `pyscript.py`.
I edited `.flake8` to turn off all the particular problems, to avoid editing the file itself.
Probably needs a better solution.

`mypy` found a couple of actual bugs.
Thanks, Python type hinting!
(Although I did chicken out with a `type: ignore` on a bytes thing in a test.)

## Could Be Better

This is very much a prototype and lots could be better.

There are still bunches of failure modes in the interceptor, and when it fails, things get _very mysterious_.
A good half-day of hardening and test-writing -- primarily unit tests -- would largely do it.
To go further, using Starlette's `FileResponse` and making an "adapter" to Playwright's `APIResponse` would help.
Starlette has likely learned a lot of lessons on file reading/responding.

Speaking of the response, this code does the minimum.
Content length?
Ha!
Again, adopting more of a regular Python web framework like Starlette (or from the old days, `webob`) would be smart.

We could speed up test running with [ideas from Pyodide Playwright ticket](https://github.com/pyodide/pyodide/issues/2048).
It looks fun to poke around on that, but the hours lost in hell discouraged me.
It's pretty fast right now, and a great improvement over the status quo.
But a 3x speedup seems interesting.

Finally, it's possible that async Playwright is the answer, for both general speedups and `wait_for_selector`.
When I first dabbled at this though, it got horrible, quickly (integrating main loops, sprinkling async/await everywhere.)
I then read something saying "don't do it unless you have to."
