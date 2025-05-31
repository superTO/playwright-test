# playwright 

## 執行步驟
1. conda env create -f environment.yml --prefix .venv
- 直接使用 environment.yml 建立虛擬環境 (會一併將套件安裝好, 所以會執行比較久)
2. conda conda activate .\.venv\
3. playwright install
4. python kickstarter.py https://www.kickstarter.com/projects/metismediarpg/astra-arcanum-the-roleplaying-game/community
- 網址自行替換

## playwright codegen execution steps
pip install playwright
playwright install

python main.py
playwright codegen https://www.kickstarter.com/
```
使用 playwright codegen 產生的程式碼會優先使用text拿資料, 不太適合用來爬蟲
```

## 使用 conda env export 匯出虛擬環境
```
conda env export > environment.yml
```