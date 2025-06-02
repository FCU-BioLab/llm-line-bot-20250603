# LINE Bot with Gemini AI and PostgreSQL

這是一個結合 Google Gemini AI 生成回應、並以 PostgreSQL 儲存訊息歷史的 LINE Bot 應用程式。

## 功能特色

- 🤖 LINE Bot 整合，支援文字訊息互動
- 🧠 使用 Google Gemini AI 生成智能回應
- 💾 PostgreSQL 資料庫儲存對話歷史
- 🔒 環境變數配置，確保安全性

## 前置需求

- Python 3.10 以上
- PostgreSQL 15 以上（本地安裝，建議搭配 pgAdmin 管理）
- pgAdmin（圖形化管理 PostgreSQL）
- ngrok
- LINE Messaging API 帳號
- Google Cloud 帳號（用於 Gemini API）

## 安裝與啟動步驟

1. **複製專案：**
   ```powershell
   git clone <repository-url>
   cd llm-linebot-demo
   ```

2. **安裝 Python 套件：**
   ```powershell
   pip install -r requirements.txt
   ```

3. **安裝 PostgreSQL 與 pgAdmin：**
   - 從 [PostgreSQL 官方網站](https://www.postgresql.org/download/windows/) 下載並安裝 PostgreSQL（建議勾選安裝 pgAdmin）。
   - 安裝完成後，啟動 pgAdmin。

4. **使用 pgAdmin 建立資料庫與用戶：**
   - 登入 pgAdmin，連線到你的 PostgreSQL 伺服器。
   - 建立新資料庫：名稱為 `yourdb`。
   - 建立新用戶（角色）：名稱為 `postgresforline`，密碼為 `password`。
   - 在 `yourdb` 資料庫中，將所有權限賦予 `postgresforline` 用戶。

5. **設定環境變數：**
   - 複製 `env.txt` 為 `.env`
   - 填入必要的環境變數：
     ```
     LINE_CHANNEL_SECRET=你的LINE_SECRET
     LINE_CHANNEL_ACCESS_TOKEN=你的LINE_TOKEN
     GEMINI_API_KEY=你的GOOGLE_GEMINI_KEY
     DATABASE_URL=postgresql://postgresforline:password@localhost:5432/yourdb
     NGROK_AUTH_TOKEN=你的NGROK_TOKEN
     MENTION_KEYWORDS=@MENTION_KEYWORDS
     ```

6. **啟動 FastAPI 服務與 ngrok（推薦用 start.bat）：**
   ```powershell
   start.bat
   ```
   或手動啟動：
   ```powershell
   uvicorn app.main:app --host 0.0.0.0 --port 8080
   ngrok http 8080
   ```

7. **設定 LINE Bot Webhook：**
   - 將 LINE Bot 的 webhook URL 設定為你的 ngrok 轉發網址 + `/callback`
   - 例如：`https://xxxxxx.ngrok.io/callback`

## 專案結構

```
llm-linebot-demo/
├── app/                    # 應用程式主要程式碼
│   ├── main.py            # FastAPI 應用程式入口
│   ├── linebot.py         # LINE Bot 處理邏輯
│   ├── memory.py          # 資料庫模型與連線
│   └── gemma_engine.py    # Gemini AI 整合
├── requirements.txt      # Python 相依套件
├── .env                 # 環境變數配置
├── start.bat            # 一鍵啟動腳本（Uvicorn + Ngrok）
└── README.md            # 專案說明
```

## 常見問題

1. **資料庫連線問題：**
   - 確認 PostgreSQL 已啟動，且 `DATABASE_URL` 設定正確
   - 可用 pgAdmin 測試連線與查詢

2. **LINE Bot 無法接收訊息：**
   - 確認 ngrok 是否正常運行
   - 檢查 webhook URL 是否正確設定
   - 確認 LINE_CHANNEL_SECRET 和 LINE_CHANNEL_ACCESS_TOKEN 是否正確

3. **ngrok 授權問題：**
   - 若第一次啟動 ngrok，請確保 `.env` 已填入 `NGROK_AUTH_TOKEN`，啟動腳本會自動授權

## 授權

MIT License