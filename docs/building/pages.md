# Content Pages

We have a home page, but we'll need some other content pages, such as "About".
Add a "Page" resource, with Markdown+frontmatter-driven content under `/pages`.


## Pages In `/pages`

- All pages will be Markdown-driven, e.g. `src/psc/pages/about.md` and `/pages/about.html`
- Install `python-frontmatter` as regular dependency
- Write tests for a new `Page` resource type and views
- Implement them
- Home page stays as a Jinja2 template, as it is heavily-Bulma (not a good candidate for Markdown)

## Navbar

- Wire `About` into the navbar

## Home Page

- Better formatting
- Content for: homepage, about, contributing, vision, homepage hero

## Future

- Images
- Static content
- Contributors
- Build command
