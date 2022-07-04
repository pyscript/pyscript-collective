"""Each example requires the same three tests:

- Test that the initial markup loads properly (currently done by testing the <title>
  tag's content)
- Testing that pyodide is loading properly
- Testing that the page contains appropriate content after rendering

The single function iterates through the examples, instantiates one playwright browser
session per example, and runs all three of each example's tests in that same browser
session.
 """

import math
import re
import time
from urllib.parse import urljoin

import pytest
from playwright.sync_api import sync_playwright

MAX_TEST_TIME = 30  # Number of seconds allowed for checking a testing condition
TEST_TIME_INCREMENT = 0.25  # 1/4 second, the length of each iteration
TEST_ITERATIONS = math.ceil(
    MAX_TEST_TIME / TEST_TIME_INCREMENT
)  # 120 iters of 1/4 second

# Content that is displayed in the page while pyodide loads
LOADING_MESSAGES = [
    "Loading runtime...",
    "Runtime created...",
    "Initializing components...",
    "Initializing scripts...",
]

EXAMPLES = [
    "hello_world",
    "p5js-minimal-demo",
]

TEST_PARAMS = {
    "hello_world": {
        "file": "hello_world.html",
        "pattern": "\\d+:\\d+:\\d+",
        "title": "PyScript Hello World",
    },
    "p5js-minimal-demo": {
        "file": "p5js-minimal-demo.html",
        "pattern": "false",
        "title": "p5.js minimal example",
    },
}


@pytest.mark.parametrize("example", EXAMPLES)
def test_examples(example, http_server):

    base_url = http_server
    example_path = urljoin(base_url, TEST_PARAMS[example]["file"])

    # Invoke playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(example_path)

        # STEP 1: Check page title proper initial loading of the example page

        expected_title = TEST_PARAMS[example]["title"]
        if isinstance(expected_title, list):
            # One example's title changes so expected_title is a list of possible
            # titles in that case
            assert page.title() in expected_title  # nosec
        else:
            assert page.title() == expected_title  # nosec

        # STEP 2: Test that pyodide is loading via messages displayed during loading

        pyodide_loading = False  # Flag to be set to True when condition met

        for _ in range(TEST_ITERATIONS):
            time.sleep(TEST_TIME_INCREMENT)
            content = page.text_content("*")
            for message in LOADING_MESSAGES:
                if message in content:
                    pyodide_loading = True
            if pyodide_loading:
                break

        assert pyodide_loading  # nosec

        # STEP 3:
        # Assert that rendering inserts data into the page as expected: search the
        # DOM from within the timing loop for a string that is not present in the
        # initial markup but should appear by way of rendering

        if TEST_PARAMS[example]["pattern"] != "false":
            re_sub_content = re.compile(TEST_PARAMS[example]["pattern"])
            py_rendered = False  # Flag to be set to True when condition met

            for _ in range(TEST_ITERATIONS):
                time.sleep(TEST_TIME_INCREMENT)
                content = page.inner_html("*")
                if re_sub_content.search(content):
                    py_rendered = True
                    break

            assert py_rendered  # nosec

        browser.close()
