from playwright.sync_api import Playwright, Page, sync_playwright, expect


def test_find_result(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://dinbendon.net/do/pub/UserManualPage")
    page.get_by_role("link", name="開始團購").click()
    page.get_by_role("link", name="公用店家").click()
    page.get_by_role("link", name="找一下").click()
    page.locator("#navigation_panel_form_term").click()
    page.locator("#navigation_panel_form_term").fill("五十")
    page.get_by_role("button", name="開始").click()
    page.get_by_text("五十嵐(內湖)", exact=True).click()
    page.locator("#navigation_panel_resultBox_shops_1").get_by_text("五十嵐(內湖)", exact=True).click()
    expect(page.locator("#navigation_panel_resultBox_shops_1")).to_contain_text("五十嵐")

    # ---------------------
    context.close()
    browser.close()

def test_value(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://dinbendon.net/do/pub/UserManualPage")
    page.get_by_role("link", name="開始團購").click()
    page.get_by_role("link", name="公用店家").click()
    page.get_by_role("link", name="找一下").click()
    page.locator("#navigation_panel_form_term").click()
    page.locator("#navigation_panel_form_term").fill("五十")
    page.get_by_role("button", name="開始").click()
    page.get_by_text("五十嵐(內湖)", exact=True).click()
    page.locator("#navigation_panel_resultBox_shops_1").get_by_text("五十嵐(內湖)", exact=True).click()
    expect(page.locator("#navigation_panel_form_term")).to_have_value("五十")

def test_failed(page: Page):
    page.goto("https://dinbendon.net/do/pub/UserManualPage")
    page.get_by_role("link", name="開始團購").click()
    page.get_by_role("link", name="公用店家").click()
    page.get_by_role("link", name="找一下").click()
    page.locator("#navigation_panel_form_term").click()
    page.locator("#navigation_panel_form_term").fill("五十")
    page.get_by_role("button", name="開始").click()
    page.get_by_text("五十嵐(內湖)", exact=True).click()
    page.locator("#navigation_panel_resultBox_shops_1").get_by_text("五十嵐(內湖)", exact=True).click()
    expect(page.locator("#navigation_panel_form_term")).to_have_value("40")

# with sync_playwright() as playwright:
    # test_find_result(playwright)
    # test_value(playwright)
