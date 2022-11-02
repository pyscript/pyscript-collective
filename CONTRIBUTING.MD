# Contributing to PyScript

Thank you for taking the time to contribute to the PyScript Collective!

This file will guide you through how to make your first community contribution, if you're looking to contribute to PyScript Core, please head over to [this](https://github.com/pyscript/pyscript) repository.

The intention set for this repository is for it to be a place that's built by the community to serve the community. We want contributors to take ownership of tasks like onboarding new folks, co-maintaining examples and supporting them, and enriching this repository with their own perspectives. It's a space for users and contributors to discuss how the community should be shaped.

## Table of contents

- **[Contributing a new example](#contributing-a-new-example)**
  - **[Recommended guidelines for an example](#recommended-guidelines-for-an-example)**
  - **[Running the tests](#running-the-tests)**
- **[Contributing a new resource](#contributing-a-new-resource)**
  - **[Recommended guidelines for a resource](#recommended-guidelines-for-a-resource)**
- **[Reporting a bug](#reporting-a-bug)**
- **[Opening an enhancement issue](#opening-an-enhancement-issue)**

### Contributing a new example

We try not to have strong boundaries in what kinds of contributions are accepted in this repository as we want contributors to be able to be as creative as they can. Still, we do have some recommendations in place so the examples in this repository offer a consistent experience to the users.

#### Recommended guidelines for an example

- Here are some great general examples of what a good contribution might be (not restrictive)

  - it showcases PyScript power to leverage other tools (either from the JavaScript or the Python ecosystem)
  - it expands on the PyScript documentation, making the use of PyScript clearer to users
  - it offers engaging educational material

- Adding meta-data

  - adding tags to your example will help us organize this repository in a much more meaningful way. Example tags come at the beginning of your main `HTML` file in the form of a comment.
  - you're also welcome to add your email or name or other forms of contact information in the header at the beginning of the file. For reference see the [example](examples/hello_world.html).

TODO Add back in `See the example examples/hello_world.html`

- Adding docs

  - PyScript strives to be accessible to beginners. If you're writing code that might be confusing, please add comments explaining your choices.
  - If you need to write further docs for your program, feel free to create a `README.md` file with instructions about installation, use, and other details on how to run your example.

#### Running the tests

To run the tests it's necessary to have a local build of PyScript running, you can learn more about it in the [PyScript docs](https://docs.pyscript.net/latest/).

Run `make test` on the root repository to run the tests locally.

Remember to have the right path set up for your `css` and `script` tags. They should point to your local build instead of PyScript's self-hosted version.

### Contributing a new resource

The PyScript Collective also welcomes contributions like blog posts, videos, video tutorials, podcasts, and all of the amazing things our community is putting out there.

The contributions in this topic are more similar to what an `awesome-page` would look like.

_If you want to add a new kind of contribution that wasn't laid out on the [README](index) yet, feel free to do so._

#### Recommended guidelines for a resource

TBD

### Reporting a bug

You can contribute a bug you found on the tests, examples, or any other technical part of the infrastructure of this repository.

Please follow the guidelines on the Issue template.

### Opening an enhancement issue

Would you like to propose an enhancement to this repository, feel free to open an enhancement proposal issue. Please follow the guidelines on the Issue template.
