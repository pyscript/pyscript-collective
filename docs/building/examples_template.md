# Examples Template

Having a template is pretty slick.
We'll now do the same for each example, but things are gonna get kinda weird: we need just part of the example's HTML.

## Example Template and Route

We'll start with a test.
We already have a `TestClient` test at `test_hello_world.test_hello_world`.
We start by adapting it to the same BeautifulSoup approach we just saw.

Next, an implementation.
We add a template at `templates/example.jinja2` then make a new `example` view and route in `app.py`.
By copying the existing view, we get something that works and, with a small test change, passes the tests.
But it's returning the contents of the home page.

Instead, we:
- Get the route parameter
- Read that file
- Use `beautifulsoup4` to extra the contents of `<main>`
- Shove that into the template as the context value of `main`

Along the way, we also extract this example's title from the `<title>` in the HTML file.
We then shove it in as the template context value of `title`.

This leaves out:
- Everything in the `<head>`, such as...loading PyScript
- All the `<py-*>` nodes elsewhere in the example's `<body>`

Uhhh...that's kind of dumb.
Why are we doing that?

## Standalone vs. Integrated vs. Unmanaged

The HTML for an example might appear in a bunch of places:

1. *Standalone*.
People want to cut-and-paste an example and run it from a `file:///` URL.
The Contributor might want to start this way. It needs the PyScript JS/CSS and possibly a `<py-config>`.
2. *Integrated Website*.
In the website, for the "best" examples, we want everything to fit together well: consistent styling, fast page transitions, using the same PyScript/Pyodide.
The Gallery should have control of these things, not the examples.
Let's call those the "integrated" examples, vs. others that need their own control.
3. *Unmanaged Website*.
These are examples on the website which need to set their own Pyodide, or not use the Gallery CSS.
4. *Integrated App*.
These are when the examples are running in the Gallery Python web app, under Starlette.
Perhaps the Contributor is browsing the example, perhaps a Coder is running the example via `pipx`.
Mostly the same as "Integrated Website".
5. *CI Builds Website*.
In this case, the example is compiled into a `public` directory and included into the website.
The example isn't really being executed.
Rather, it's being assembled into output.

At this point, we're still in "Integrated App".
The Starlette process wants an "integrated" example, where the CSS/JS/Pyodide is under the `layout.jinja2` control.
All the "integrated" examples will look and feel consistent.

## Extra PyScript Stuff in Head

With that said, an "integrated" examples might have other static assets to go in the `<head>`: extra CSS, for example.
We'll add that to our example.

Remember, these examples are "standalone".
They include the `<link>` and `<script>` pointing to PyScript.
We don't want *those* -- they come from `layout.jinja2`.
We *do* want anything else them put in there, with relative links as the targets.

Let's write a failing first for including `hello_world.css`.
For implementation:
- Add a slot in `layout.jinja2`
- Change `example.jinja2` to fill that slot, based on passed in string
- Pass in a string of all the HTML to include
- Build that string from a `beautifulsoup` `select`

## Example Template Needs `<py-config>`

We want the HTML for the examples to get a Gallery-managed `<py-config>`.
But we don't want this in other, non-example pages.
We'll add an `extra_body` slot in `layout.jinja2`, then fill it from `example.jinja2`.

Starting, of course, with a test.

## Plucking Example Parts

That's good for stuff in the `<head>`.
But we have a problem in the `<body>`.
PyScript only allows `<py-script>` as a direct child of `<body>`, so we can't put it in `<main>`.
We need a policy like this:

- Anything in the example's "UI" (the DOM) goes in `<main>` and gets copied over
- Any `<py-*>` nodes directly under `<body>` get copied over
- *Except* `<py-config>`
- Everything else in `<body>` is left out

We'll write some tests:
- Ensure only one `<py-config>` with a runtime pointed to our local Pyodide
- The `<py-script>` is copied over, in the right spot
- Some tracer `<h6>` that is *outside* of `<main>` is *not* copied over

## QA

`mypy` gave us some trouble at the end, because `beautifulsoup` has some unusual typing.
We thus moved the `example` view's soup filtering into a standalone function which had a `cast`.

## Future

This is actually pretty neat.
But the view is doing too much.
Later, we'll introduce a "resource" concept, kind of like a model, and move the work there.
