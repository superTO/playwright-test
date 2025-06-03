import argparse
import random
import time
from typing import List
from playwright.sync_api import Playwright, sync_playwright
# from playwright_stealth import stealth_sync, StealthConfig

def run(playwright: Playwright, initial_url: str) -> List[str|None]:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    # context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36")
    page = context.new_page()

    ## 太多驗證啦
    # 因為重開browser所以不用了
    # stealth_config = StealthConfig(
    #     webdriver=True,
    #     webgl_vendor=True,
    #     chrome_app=True,
    #     chrome_csi=True,
    #     chrome_load_times=True,
    #     chrome_runtime=True,
    #     iframe_content_window=True,
    #     media_codecs=True,
    #     navigator_hardware_concurrency=4,
    #     navigator_languages=True,
    #     navigator_permissions=True,
    #     navigator_platform=True,
    #     navigator_plugins=True,
    #     navigator_user_agent=True,
    #     navigator_vendor=True,
    #     outerdimensions=True,
    #     hairline=True,
    #     vendor='Google Inc.',
    #     renderer='Intel Iris OpenGL Engine',
    #     nav_vendor='Google Inc.',
    #     nav_user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    #     nav_platform="Win32",
    #     languages=('en-US', 'en'),
    #     runOnInsecureOrigins=None
    # )

    # stealth_sync(page, config=stealth_config)

    page.goto(initial_url)

    # time.sleep(random.uniform(1, 5)) # 等1~5秒
    # 先判斷是不是US再決定要不要爬
    # page.get_by_role("link", name="United States").first.click()

    # elements = page.locator(".secondary-text.js-location-secondary-text a:has-text('United States')").all()
    elements = page.locator(".secondary-text.js-location-secondary-text").all()
    href_list = []
    for element in elements:
        # print(element.all_inner_texts())
        if element.all_inner_texts()[0] != 'United States':
            href_list.append(None)
        else:
            # 向上2層
            parent = element.locator("xpath=../..")
            # print(parent.all_inner_texts())
            # 在同一層找 .primary-text.js-location-primary-text 並click第一個match項目
            primary_text_element = parent.locator(".primary-text.js-location-primary-text").first
            # print(primary_text_element.all_inner_texts())
            ## 拿取 html a element
            link_element = primary_text_element.locator("a").first
            href = link_element.get_attribute("href")
            href_list.append(href)
    
    # print(href_list)
    # ---------------------
    context.close()
    browser.close()
    return href_list

# 驗證太煩了, 每次都重開一個新個browser
def run2(playwright: Playwright, href_list: List) -> List[str|None]:
    location = []
    for href in href_list:
        if href is None:
            location.append(None)
        else:
            browser = playwright.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()

            full_url = "https://www.kickstarter.com" + href

            page.goto(full_url)
            # 因為重開browser所以不用等了
            # time.sleep(random.uniform(1, 5)) # 等1~5秒

            location_span = page.locator("#location_filter .js-title").first
            location_text = location_span.inner_text()
            location.append(location_text)
            # print(f"当前选择的地点是: {location_text}")
            context.close()
            browser.close()
    
    return location


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kickstarter Location Scraper")
    parser.add_argument("url", help="The initial URL to start with")
    args = parser.parse_args()

    with sync_playwright() as playwright:
        href_list = run(playwright, args.url)
        print(href_list)
        location_text_list = run2(playwright, href_list)
        print(location_text_list)
    


