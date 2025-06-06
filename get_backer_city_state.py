import pandas as pd
import sqlite3
import time
from typing import List
from playwright.sync_api import Playwright, sync_playwright
# from playwright_stealth import stealth_sync, StealthConfig

def run(playwright: Playwright, initial_url: str) -> List[str|None]:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    # context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36")
    page = context.new_page()

    page.goto(initial_url)
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
    
    while len(href_list) < 10:  href_list.append(None)  
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

# --- 自動偵測起始索引的函式 ---
def get_start_index(connection, table_name):
    """
    檢查資料庫，返回下一個要處理的索引值。
    """
    try:
        # 讀取已儲存資料中的最大索引值
        # "index" 是 pandas.to_sql 預設建立的索引欄位名稱
        last_idx_df = pd.read_sql(f'SELECT MAX("index") FROM {table_name}', connection)
        last_idx = last_idx_df.iloc[0, 0]

        if pd.notna(last_idx):
            # 如果找到了，就從下一筆開始
            start_from = int(last_idx) + 1
            print(f"資料庫中最後一筆已處理的索引為: {last_idx}。將從索引 {start_from} 開始執行。")
            return start_from
        else:
            # 如果表格是空的，從頭開始
            print(f"資料表 '{table_name}' 為空，將從頭開始執行。")
            return 0
    except (sqlite3.OperationalError, pd.io.sql.DatabaseError):
        # 如果資料表不存在，也是從頭開始
        print(f"找不到資料表 '{table_name}'，將建立新表並從頭開始執行。")
        return 0

if __name__ == "__main__":
    file_link = "filepath.csv"
    df = pd.read_csv(file_link)

    # Construct new variable
    df = df.assign(backer_detail_city1 = None
                , backer_detail_city2 = None
                , backer_detail_city3 = None
                , backer_detail_city4 = None
                , backer_detail_city5 = None
                , backer_detail_city6 = None
                , backer_detail_city7 = None
                , backer_detail_city8 = None
                , backer_detail_city9 = None
                , backer_detail_city10 = None)

    con_out = sqlite3.connect("filepath.db")   
    c = con_out.cursor()

    # --- MODIFIED: 自動設定起始點，不再需要手動的 hand_type ---
    start_index = get_start_index(con_out, "backer_location")
    is_first_write = (start_index == 0) # 判斷是否為首次寫入

    # Set batch processing parameters
    threshold = 1  # number of rows per batch
    # hand_type = 228  # resume point if interrupted (set to None or 0 to start from beginning)

    # start_index = hand_type if hand_type else 0
    total_rows = len(df)
    
    # 加入sleep防止被ban IP
    count = 30

    for i in range(start_index, total_rows):
        count = count - 1
        if count == 0:
            count = 5
            time.sleep(1*60)
        
        BackerCount = int(df.at[i, 'backers_count'])
        url = df.at[i, 'urls_web_project'].replace('?ref=discovery_category_newest', '/community')\
                                          .replace('?ref=category_newest', '/community')

        if BackerCount >= 10:
            print(f'Index {i}, Backer_count = {BackerCount}')
            with sync_playwright() as playwright:
                print(url)
                href_list = run(playwright, url)
                location_text_list = run2(playwright, href_list)
                print(location_text_list)

            if location_text_list and len(location_text_list) == 10:
                for j in range(10):
                    df.at[i, f'backer_detail_city{j+1}'] = location_text_list[j]
            else:
                print(f"Empty or invalid list at index {i}")
                for j in range(10):
                    df.at[i, f'backer_detail_city{j+1}'] = ""
        else:
            for j in range(10):
                df.at[i, f'backer_detail_city{j+1}'] = ""

        # --- MODIFIED: 批次寫入資料庫的邏輯 ---
        if ((i + 1) % threshold == 0) or (i == total_rows - 1):
            # 因為 threshold=1，所以每次只選取當前這一行
            output = df.loc[i:i] 
            
            # 決定寫入模式
            write_mode = 'replace' if is_first_write else 'append'
            
            try:
                # --- IMPORTANT: index=True 是實現自動續爬的關鍵 ---
                # 它會將 DataFrame 的索引 (0, 1, 2...) 作為一欄存入資料庫
                output.to_sql("backer_location", con=con_out, if_exists=write_mode, index=True)
                
                print(f'---- 已將索引 {i} 的資料寫入資料庫 (模式: {write_mode}) ----')
                
                # 第一次成功寫入後，之後的模式都必須是 'append'
                if is_first_write:
                    is_first_write = False
            except Exception as e:
                print(f"索引 {i} 寫入資料庫時發生錯誤: {e}")
                # 這裡可以加入更詳細的錯誤處理，例如重試或記錄 log
                break # 發生嚴重錯誤時可以選擇中斷迴圈

    con_out.close()