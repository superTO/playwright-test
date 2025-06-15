import pandas as pd
import sqlite3
import os

def copy_db_table_exclude_specific_ids(source_db_path, target_db_path, table_name,
                                        columns_to_exclude=["index", "id", "row"]):
    """
    從來源資料庫的指定表格中讀取資料，排除指定的ID/索引欄位，
    並將剩餘資料寫入目標資料庫的相同表格中，不包含 Pandas 自動生成的 'index' 欄位。
    目標表格的結構將根據來源表格的非排除欄位自動建立。

    Args:
        source_db_path (str): 來源 .db 檔案的路徑 (例如 'backer_city_1.db')。
        target_db_path (str): 目標 .db 檔案的路徑 (例如 'new_backer_city_1.db')。
        table_name (str): 要操作的表格名稱 (例如 'backer_location')。
        columns_to_exclude (list): 一個字串列表，包含在複製時要從來源表格中排除的欄位名稱。
                                   預設排除 "index", "id", "row"。
    """
    if not os.path.exists(source_db_path):
        print(f"錯誤：來源資料庫檔案不存在：{source_db_path}")
        return

    # 刪除目標檔案（如果存在），以確保每次都是全新的建立
    if os.path.exists(target_db_path):
        os.remove(target_db_path)
        print(f"已移除舊的目標資料庫檔案: {target_db_path}")

    conn_source = None
    conn_target = None
    try:
        # 1. 連接到來源資料庫並獲取表格結構
        conn_source = sqlite3.connect(source_db_path)
        cursor_source = conn_source.cursor()

        # 檢查來源表格是否存在
        cursor_source.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
        if cursor_source.fetchone() is None:
            print(f"錯誤：來源資料庫 '{source_db_path}' 中不存在表格 '{table_name}'。")
            conn_source.close()
            return

        # 獲取來源表格的所有欄位資訊
        cursor_source.execute(f"PRAGMA table_info({table_name});")
        source_columns_info = cursor_source.fetchall()

        # 篩選出要複製的欄位及其類型
        # 這裡會排除你指定的所有 ID/索引相關的欄位
        columns_to_copy_with_type = []
        columns_to_copy_names = []
        excluded_found = []

        for col in source_columns_info:
            col_name = col[1]  # 欄位名稱
            col_type = col[2]  # 欄位類型

            if col_name.lower() in [ex_col.lower() for ex_col in columns_to_exclude]:
                excluded_found.append(col_name)
                continue # 跳過這個欄位，不將它加入複製列表

            columns_to_copy_with_type.append(f'"{col_name}" {col_type}')
            columns_to_copy_names.append(f'"{col_name}"') # 在SQL查詢中使用帶引號的欄位名

        if not columns_to_copy_names:
            print(f"錯誤：在來源資料庫 '{source_db_path}' 的 '{table_name}' 表格中未找到可複製的非排除欄位。")
            conn_source.close()
            return

        print(f"來源表格 '{table_name}' 偵測到的欄位 (共 {len(source_columns_info)} 個)：{[col[1] for col in source_columns_info]}")
        print(f"將排除的欄位：{excluded_found}")

        # 2. 從來源資料庫讀取資料 (只讀取非排除欄位)
        # print(f"正在從 '{source_db_path}' 的 '{table_name}' 表格讀取資料...")
        select_sql = f"SELECT {','.join(columns_to_copy_names)} FROM {table_name}"
        df = pd.read_sql_query(select_sql, conn_source)
        conn_source.close()
        print(f"已讀取 {len(df)} 筆資料。")

        # 3. 將 DataFrame 寫入新的資料庫
        conn_target = sqlite3.connect(target_db_path)
        print(f"正在將資料寫入 '{target_db_path}' 的 '{table_name}' 表格 (確保不包含排除的 ID/索引欄位)...")

        # 創建目標表格的 SQL 語句
        # 我們不為新表格定義主鍵，讓 SQLite 自動管理隱含的 rowid
        # 如果你需要一個明確的自增ID（例如名為 'new_id'），可以手動加入：
        # create_table_sql = f'''
        #     CREATE TABLE IF NOT EXISTS {table_name} (
        #         new_id INTEGER PRIMARY KEY AUTOINCREMENT,
        #         {','.join(columns_to_copy_with_type)}
        #     );
        # '''
        create_table_sql = f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                {','.join(columns_to_copy_with_type)}
            );
        '''
        cursor_target = conn_target.cursor()
        cursor_target.execute(create_table_sql) # 確保表格結構正確
        conn_target.commit()

        # 核心：使用 index=False 避免寫入 DataFrame 的索引 (即 Pandas 自動生成的索引)
        # if_exists='append' 將資料新增到現有表格。
        # 如果你想每次都清空並重建表格，可以使用 'replace'。
        df.to_sql(table_name, conn_target, if_exists='append', index=False)
        conn_target.close()

        print(f"資料已成功複製到 '{target_db_path}' 的 '{table_name}' 表格中。")
        print(f"'{target_db_path}' 中的 '{table_name}' 表格現在不包含原始來源中的指定排除欄位。")

    except Exception as e:
        print(f"操作過程中發生錯誤：{e}")
        if conn_source:
            conn_source.close()
        if conn_target:
            conn_target.close()

# --- 執行範例 ---
if __name__ == "__main__":
    # 你的來源 .db 檔案名稱
    source_db_file = "backer_city_1.db"
    # 你想生成的新 .db 檔案名稱
    target_db_file = "new_" + source_db_file
    # 你想操作的表格名稱
    table_to_copy = "backer_location"

    # 要排除的欄位列表。根據你提供的來源結構，我們排除 "index", "id", "row"。
    # 你可以根據需要修改這個列表。
    columns_to_exclude_from_source = ["index"]

    # 1. 建立一個範例的 source_db_file (如果你還沒有的話)
    # 此範例數據用於測試。如果你的 backer_city_1.db 已存在，這段程式碼將會跳過。
    print("--- 準備範例來源資料庫 (backer_city_1.db) ---")
    if not os.path.exists(source_db_file):
        conn_temp = sqlite3.connect(source_db_file)
        cursor_temp = conn_temp.cursor()
        cursor_temp.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_to_copy} (
                "index" INTEGER,
                "id" INTEGER,
                "backers_count" INTEGER,
                "urls_web_project" TEXT,
                "row" INTEGER,
                "backer_detail_city1" TEXT,
                "backer_detail_city2" TEXT,
                "backer_detail_city3" TEXT,
                "backer_detail_city4" TEXT,
                "backer_detail_city5" TEXT,
                "backer_detail_city6" TEXT,
                "backer_detail_city7" TEXT,
                "backer_detail_city8" TEXT,
                "backer_detail_city9" TEXT,
                "backer_detail_city10" TEXT
            );
        ''')
        conn_temp.commit()
        conn_temp.close()
        print(f"已創建範例來源資料庫 '{source_db_file}'。")
    else:
        print(f"範例來源資料庫 '{source_db_file}' 已存在。")

    print("\n--- 開始複製資料並移除指定欄位 ---")
    copy_db_table_exclude_specific_ids(source_db_file, target_db_file, table_to_copy,
                                       columns_to_exclude=columns_to_exclude_from_source)
    print("--- 複製完成 ---")

    # 2. 驗證新生成的資料庫內容 (可選)
    print(f"\n--- 驗證 '{target_db_file}' 中的 '{table_to_copy}' 表格內容 ---")
    try:
        conn_check = sqlite3.connect(target_db_file)
        cursor_check = conn_check.cursor()

        # 獲取表格的欄位資訊
        cursor_check.execute(f"PRAGMA table_info({table_to_copy});")
        columns = [col[1] for col in cursor_check.fetchall()]
        print(f"'{table_to_copy}' 表格中的欄位: {columns}(共 {len(columns)} 個)") # 應不包含 "index", "id", "row"

        # 讀取所有資料，查看 SQLite 自動生成的 rowid
        cursor_check.execute(f"SELECT rowid, * FROM {table_to_copy};")
        rows = cursor_check.fetchall()
        # for row in rows:
            # print(row)
        conn_check.close()
    except Exception as e:
        print(f"驗證資料庫時發生錯誤: {e}")

    # 3. 清理範例檔案 (可選)
    # try:
    #     os.remove(source_db_file)
    #     os.remove(target_db_file)
    #     print(f"\n已刪除範例檔案：{source_db_file}, {target_db_file}")
    # except OSError as e:
    #     print(f"刪除檔案時發生錯誤: {e}")