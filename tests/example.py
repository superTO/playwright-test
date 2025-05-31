import re
from playwright.sync_api import Page, expect

def test_has_title(page: Page):
    page.goto("https://playwright.dev/")

    # Expect a title "to contain" a substring.
    expect(page).to_have_title(re.compile("Playwright"))

def test_get_started_link(page: Page):
    page.goto("https://playwright.dev/")

    # Click the get started link.
    page.get_by_role("link", name="Get started").click()

    # Expects page to have a heading with the name of Installation.
    expect(page.get_by_role("heading", name="Installation")).to_be_visible()

def test_something(page: Page):
    page.goto("https://playwright.dev/python/docs/intro")
    expect(page.get_by_role("article")).to_contain_text("Playwright was created specifically to accommodate the needs of end-to-end testing. Playwright supports all modern rendering engines including Chromium, WebKit, and Firefox. Test on Windows, Linux, and macOS, locally or on CI, headless or headed with native mobile emulation.")
    expect(page.get_by_role("article")).to_match_aria_snapshot("- paragraph:\n  - text: Create a file that follows the\n  - code: test_\n  - text: prefix convention, such as\n  - code: test_example.py\n  - text: \", inside the current working directory or in a sub-directory with the code below. Make sure your test name also follows the\"\n  - code: test_\n  - text: prefix convention.")

def test_wrong_title(page: Page):
    page.goto("https://playwright.dev/")

    # 這個斷言會失敗，因為頁面標題不會包含 "Wrong Title"
    expect(page).to_have_title(re.compile("Wrong Title"))
