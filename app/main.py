# 載入環境變數
from dotenv import load_dotenv

load_dotenv()

# 導入必要的 FastAPI 和 LINE Bot 相關模組
from fastapi import FastAPI, Request, Header
from linebot.exceptions import InvalidSignatureError
from app.linebot import handle_events
from app.memory import init_db, wait_for_db
import os
from linebot import WebhookHandler

# 建立 FastAPI 應用程式實例
app = FastAPI()
# 初始化 LINE Bot 處理器，使用環境變數中的 Channel Secret
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# 等待資料庫服務啟動並初始化資料庫
wait_for_db()  # 等待資料庫啟動
init_db()      # 初始化資料庫

# 定義 LINE Bot 的 webhook 端點
@app.post("/callback")
async def callback(request: Request, x_line_signature: str = Header(None)):
    # 取得請求內容
    body = await request.body()
    try:
        # 驗證並處理 LINE 訊息
        handler.handle(body.decode("utf-8"), x_line_signature)
    except InvalidSignatureError:
        # 簽章驗證失敗時回傳錯誤訊息
        return {"message": "Invalid signature"}
    # 處理成功時回傳 OK
    return {"message": "OK"}

# 註冊 LINE Bot 事件處理器
handle_events(handler)