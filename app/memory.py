from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import OperationalError
from datetime import datetime
import time
import os

# 從環境變數讀取資料庫連線字串（在 .env 裡定義）
DATABASE_URL = os.getenv("DATABASE_URL")

# 建立 SQLAlchemy 引擎與 session
# pool_pre_ping=True 確保連線池中的連線都是有效的
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
# 建立資料庫 session 工廠
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 宣告模型基礎類別，用於定義資料表結構
Base = declarative_base()

# --- 資料表定義 ---

class Message(Base):
    """訊息記錄資料表
    
    用於儲存使用者和 AI 助手的對話歷史
    """
    __tablename__ = "memory"

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主鍵，自動遞增
    sender_id = Column(String)  # 使用者 ID
    role = Column(String)  # 訊息角色："user" 或 "assistant"
    content = Column(Text)  # 訊息內容
    timestamp = Column(DateTime, default=datetime.utcnow)  # 訊息時間戳

class UserState(Base):
    """使用者狀態資料表
    
    用於儲存使用者的設定狀態
    """
    __tablename__ = "user_state"

    sender_id = Column(String, primary_key=True)  # 使用者 ID（主鍵）
    mention_mode = Column(Boolean, default=False)  # 提醒模式開關

# --- 初始化資料庫 ---

def init_db():
    """初始化資料庫，建立所有資料表"""
    Base.metadata.create_all(bind=engine)

# --- 等待資料庫 ---

def wait_for_db(max_retries=10, delay=2):
    """重試等待資料庫啟動
    
    Args:
        max_retries (int): 最大重試次數
        delay (int): 每次重試間隔秒數
    
    Raises:
        Exception: 當資料庫無法連線時拋出異常
    """
    for i in range(max_retries):
        try:
            with engine.connect() as conn:
                return  # 成功就結束
        except OperationalError:
            print(f"[wait_for_db] 資料庫尚未啟動，重試中... ({i + 1}/{max_retries})")
            time.sleep(delay)
    raise Exception("資料庫啟動失敗，請確認 db 服務")

# --- 資料操作方法 ---

def save_message(sender_id: str, role: str, content: str):
    """儲存訊息，並保留該使用者最近的 7 則訊息
    
    Args:
        sender_id (str): 使用者 ID
        role (str): 訊息角色
        content (str): 訊息內容
    """
    db = SessionLocal()
    try:
        # 新增訊息
        message = Message(sender_id=sender_id, role=role, content=content)
        db.add(message)
        db.commit()

        # 刪除舊訊息，只保留最近 7 則
        messages = db.query(Message)\
            .filter(Message.sender_id == sender_id)\
            .order_by(Message.timestamp.desc())\
            .offset(7).all()
        for m in messages:
            db.delete(m)
        db.commit()
    finally:
        db.close()

def get_history(sender_id: str):
    """取得該使用者的歷史訊息（按時間排序）
    
    Args:
        sender_id (str): 使用者 ID
    
    Returns:
        list: 訊息歷史列表，每則訊息包含 role 和 content
    """
    db = SessionLocal()
    try:
        # 查詢並按時間排序
        messages = db.query(Message)\
            .filter(Message.sender_id == sender_id)\
            .order_by(Message.timestamp.asc())\
            .all()
        return [{"role": m.role, "content": m.content} for m in messages]
    finally:
        db.close()

def clear_history(sender_id: str):
    """清除該使用者的所有訊息紀錄
    
    Args:
        sender_id (str): 使用者 ID
    """
    db = SessionLocal()
    try:
        # 刪除所有訊息
        db.query(Message).filter(Message.sender_id == sender_id).delete()
        db.commit()
    finally:
        db.close()
