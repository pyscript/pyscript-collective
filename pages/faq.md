---
title: FAQ
subtitle: Questions about the Collective, the Gallery, the examples...answered.
---

The Collective...it's kind of an odd little ducky.
The Gallery?
Ditto.

Let's answer some questions.

# Why should I care?

- A slick, supported web app for browsing quality examples
- A cool, fast testing regime with `TestClient` plus Playwright *interceptors*
- An installable package to run/hack examples without needing a network connection
- No `package.json`
- Hands-free GitHub Actions

# Gallery

The Gallery is the web application and static website for browsing examples, contributors, etc.

### Why bundle your own everything?

The Gallery has a fork of PyScript and -- you heard it right -- a private copy of Pyodide.
Why?

To let us run offline or in low-bandwidth settings.
When I wrote the Gallery, I was on a *slow* connection.
It was super-painful.
Consuming the Gallery and contributing should be more joyful.

Also, we want a stable checkpoint in time.
The examples will work against a known set of stuff, because we'll bundle that set of stuff.

If you're interested in such stuff, take a look at the docs for the prototype repo.
In there is a step-by-step diary of the journey taken for all of these decisions.

### What's up with testing?

Well, glad you asked!
I'm a big fan of test-first.
The existing PyScript testing regime has some rough edges and I wanted to explore alternatives and propose changes.

The Collective will have to stand behind the Gallery and the examples.
We need it to be productive.

### No `pyscript.css`?

Yep, the Gallery and the website don't use the PyScript styling.
The PyScript core team doesn't plan to force folks to use PyScript itself as the application.
The Gallery is an exemplar of that ethos.
It's an app that made some choices.

### Why Bulma?

Cuz I like it.
And I know it.
I wanted a mature, off-the-shelf style package that looks great without me thinking.
And if I want more, I get the SASS package and hack away.

But perhaps you noticed -- there's no `package.json` here.
No tooling.
Pleasureville.

### PWA offline-first?

Wouldn't it be cool to work offline, like an installable app on a mobile device?
It could happen!
Maybe with `htmx` to smooth page changes.

Why stop there?
Let's have a hot-reloading Gallery that pushes incremental changes to fragments over SSE.

# Examples

Examples are the heart of the Gallery and Collective.

### Why all that tooling crap!?!

`mypy` and type hints? `Flake8`? `nox`? GitHub Actions? Are you *insane*?

You know what's insane?
The answer to the next question.
Yes, the tooling is a tax, and we're open to lowering taxes.
But taxes serve the public good, and our job is to deliver a Gallery that works, now in the future...based on examples from *other people*.

To some degree, it's also a teaching tool for "best practices."
But that -- like "Pythonic" -- is an expression sure to get an eye-roll.
So consider the "we want examples that are good teaching tools" as a secondary benefit.

### Wait, YOU are going to hold the bag...forever? Thanks!

Yes, when an example is accepted, the people in the Collective promise to co-own it.
Keep it working, fix bugs people report, rebuild Frankenstein when PyScript/Pyodide go off in some new direction.
It's there on the tin: "Collective".
We're all in this together.

### Oh, you're tricking me into joining!

Yep, freely admitted.
We want a fun, joyous place where Python newcomers feel valued and valuable.
We want your example -- but we also want *you*!

There's lots we can teach you.
Managing Git, releasing packages, writing tests, fighting `mypy`.
As well as the Gallery itself -- add new features, help write tests, make videos.

In a perfect world, "Collaborator for the PyScript Collective" will be a treasured listing on your LinkedIn profile.
You'll use us for a job reference, and we'll get you a sweet career upgrade.

In exchange, we'll ask you to help us trick the next person into joining the Collective, then "coach them up" to being a star and moving to a better job.

No, no, no...this does NOT sound like a Ponzi scheme.
