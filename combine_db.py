import sqlite3
import os
import pandas as pd

def merge_sqlite_databases(source_db_paths, target_db_path, table_name):
    """
    將多個 SQLite 資料庫檔案中的特定表格合併到一個新的目標資料庫檔案中。
    會自動處理目標表格的創建（基於第一個來源的結構），並將後續資料附加。

    Args:
        source_db_paths (list): 包含所有要合併的來源 .db 檔案路徑的列表。
        target_db_path (str): 合併後的目標 .db 檔案的路徑和名稱。
        table_name (str): 要從每個來源資料庫中合併的表格名稱 (例如 'backer_location')。
    """
    if not source_db_paths:
        print("錯誤：來源資料庫路徑列表不能為空。")
        return

    # 確保目標檔案是全新的，避免混淆
    if os.path.exists(target_db_path):
        os.remove(target_db_path)
        print(f"已移除舊的目標資料庫檔案: {target_db_path}")

    conn_target = None
    try:
        conn_target = sqlite3.connect(target_db_path)
        cursor_target = conn_target.cursor()

        # 遍歷所有來源資料庫
        for i, source_db_path in enumerate(source_db_paths):
            if not os.path.exists(source_db_path):
                print(f"警告：來源資料庫檔案不存在，跳過：{source_db_path}")
                continue

            conn_source = None
            try:
                conn_source = sqlite3.connect(source_db_path)
                cursor_source = conn_source.cursor()

                # 檢查來源表格是否存在
                cursor_source.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
                if cursor_source.fetchone() is None:
                    print(f"警告：來源資料庫 '{source_db_path}' 中不存在表格 '{table_name}'，跳過。")
                    continue

                if i == 0: # 處理第一個來源資料庫，用來創建目標表格結構
                    print(f"使用 '{source_db_path}' 的 '{table_name}' 表格結構來初始化目標資料庫。")
                    cursor_source.execute(f"PRAGMA table_info({table_name});")
                    source_columns_info = cursor_source.fetchall()

                    # 構建 CREATE TABLE 語句 (不包含任何ID欄位，只有資料欄位)
                    columns_schema = []
                    column_names_for_select = []
                    for col in source_columns_info:
                        col_name = col[1]
                        col_type = col[2]
                        columns_schema.append(f'"{col_name}" {col_type}')
                        column_names_for_select.append(f'"{col_name}"')

                    if not columns_schema:
                        print(f"錯誤：來源資料庫 '{source_db_path}' 的 '{table_name}' 表格中沒有可複製的欄位，無法創建目標表格。")
                        conn_source.close()
                        continue

                    create_table_sql = f'''
                        CREATE TABLE {table_name} (
                            {','.join(columns_schema)}
                        );
                    '''
                    cursor_target.execute(create_table_sql)
                    conn_target.commit()
                    print(f"已在 '{target_db_path}' 中創建 '{table_name}' 表格。")

                # 從來源讀取所有資料
                print(f"正在從 '{source_db_path}' 讀取資料並附加到 '{target_db_path}'...")
                # 再次獲取欄位名，因為第一個檔案可能創建了，後面的檔案也需要匹配
                # 確保我們只選擇正確的資料欄位，忽略任何可能的隱藏ID
                cursor_source.execute(f"PRAGMA table_info({table_name});")
                current_source_columns = [f'"{col[1]}"' for col in cursor_source.fetchall()]
                
                # 過濾掉可能仍然存在的 Pandas 遺留 "index" 欄位，或者其他不應該被 SELECT 的欄位
                # 這裡假設你的 new_backer_city_X.db 已經是乾淨的，沒有 "index", "id", "row" 這些了
                # 所以我們只選擇所有存在的欄位
                
                df = pd.read_sql_query(f"SELECT {','.join(current_source_columns)} FROM {table_name}", conn_source)

                # 將資料附加到目標資料庫
                # if_exists='append' 是關鍵，它將新資料加到現有表格末尾
                # index=False 確保 Pandas 不會自動添加 DataFrame 索引
                df.to_sql(table_name, conn_target, if_exists='append', index=False)
                conn_target.commit() # 每次處理完一個檔案就提交，確保進度
                print(f"已成功從 '{source_db_path}' 合併 {len(df)} 筆資料。")

            except sqlite3.Error as e:
                print(f"處理 '{source_db_path}' 時發生資料庫錯誤：{e}")
                # 不回滾，嘗試繼續處理下一個文件
            except Exception as e:
                print(f"處理 '{source_db_path}' 時發生非資料庫錯誤：{e}")
            finally:
                if conn_source:
                    conn_source.close()

    except sqlite3.Error as e:
        print(f"主資料庫操作錯誤：{e}")
        if conn_target:
            conn_target.rollback()
    except Exception as e:
        print(f"合併過程中發生總體錯誤：{e}")
    finally:
        if conn_target:
            conn_target.close()
    
    print(f"所有指定資料庫的 '{table_name}' 表格已合併到 '{target_db_path}'。")

# --- 使用範例 ---
if __name__ == "__main__":
    # 創建 new_backer_city_1.db 到 new_backer_city_7.db
    mock_db_names = []
    base_table_name = "backer_location"
    for i in range(1, 8): # 1 到 7
        db_file = f"new_backer_city_{i}.db"
        mock_db_names.append(db_file)

    # --- 實際合併操作 ---
    print("\n--- 開始合併多個資料庫檔案 ---")
    final_merged_db = "merged_backer_data.db"
    merge_sqlite_databases(mock_db_names, final_merged_db, base_table_name)
    print("--- 合併完成 ---")

    # --- 驗證合併後的資料庫內容 (可選) ---
    print(f"\n--- 驗證 '{final_merged_db}' 中的 '{base_table_name}' 表格內容 ---")
    try:
        conn_check = sqlite3.connect(final_merged_db)
        cursor_check = conn_check.cursor()

        cursor_check.execute(f"PRAGMA table_info({base_table_name});")
        columns = [col[1] for col in cursor_check.fetchall()]
        print(f"合併後表格 '{base_table_name}' 的欄位: {columns}")

        cursor_check.execute(f"SELECT rowid, * FROM {base_table_name};")
        rows = cursor_check.fetchall()
        print(f"合併後表格 '{base_table_name}' 共有 {len(rows)} 筆資料。")
        # 打印前幾條和後幾條，避免輸出過多
        for row_data in rows[:10]: # 只打印前10條
            print(row_data)
        if len(rows) > 10:
            print("...")
            for row_data in rows[-5:]: # 打印後5條
                print(row_data)
        
        conn_check.close()
    except Exception as e:
        print(f"驗證合併資料庫時發生錯誤: {e}")

    # --- 清理模擬檔案 (可選) ---
    # for db_file in mock_db_names:
    #     if os.path.exists(db_file):
    #         os.remove(db_file)
    # if os.path.exists(final_merged_db):
    #     os.remove(final_merged_db)
    # print("\n已清理所有模擬和合併後的資料庫檔案。")