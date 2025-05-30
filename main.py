import re
from playwright.sync_api import sync_playwright, Page, expect

def run_playwright_test(page: Page):
    """
    執行 Playwright 測試步驟。
    """
    print("開始 Playwright 測試...")

    # 1. 打開 Playwright 官方網站
    print("正在導覽至 https://playwright.dev/ ...")
    page.goto("https://playwright.dev/")

    # 2. 檢查頁面標題是否包含 "Playwright"
    print("正在檢查頁面標題...")
    expect(page).to_have_title(re.compile("Playwright"))
    print(f"頁面標題 '{page.title()}' 符合預期。")

    # 3. 點擊導覽列中的 "Docs" 連結
    print("正在點擊 'Docs' 連結...")
    # 使用 get_by_role 來定位連結
    docs_link = page.get_by_role("link", name="Docs")
    docs_link.click()
    print("'Docs' 連結已點擊。")

    # 4. 等待 "Installation" 文字出現在頁面上
    print("正在等待 'Installation' 文字出現...")
    # locator 方法可以用來定位元素，並使用 expect 等待其可見
    installation_text = page.locator("h1:has-text('Installation')") # 更精確的定位到 h1 標籤中的 Installation
    expect(installation_text).to_be_visible(timeout=10000) # 設定等待超時時間為 10 秒
    print("'Installation' 文字已找到。")

    # 5. 截取目前頁面的螢幕截圖並儲存
    screenshot_path = "playwright_direct_run_example.png"
    print(f"正在截取螢幕截圖並儲存至 {screenshot_path} ...")
    page.screenshot(path=screenshot_path)
    print(f"螢幕截圖已儲存至 {screenshot_path}")

    print("Playwright 測試完成！")

# 主執行區塊
if __name__ == "__main__":
    with sync_playwright() as p:
        # 啟動瀏覽器，可以選擇 chromium, firefox, or webkit
        # headless=False 會顯示瀏覽器操作過程，方便調試
        # headless=True (預設) 會在背景執行，不顯示 UI
        print("正在啟動瀏覽器...")
        browser = p.chromium.launch(headless=False)
        # browser = p.firefox.launch(headless=False)
        # browser = p.webkit.launch(headless=False)

        # 建立一個新的瀏覽器分頁
        page = browser.new_page()

        try:
            # 執行測試函數
            run_playwright_test(page)
        except Exception as e:
            print(f"測試過程中發生錯誤: {e}")
        finally:
            # 確保瀏覽器最後一定會關閉
            print("正在關閉瀏覽器...")
            browser.close()
            print("瀏覽器已關閉。")