from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import re
# from app.deepseek_engine import ask_deepseek
from app.gemma_engine import query_gemini
from app.memory import save_message, get_history, clear_history, get_today_message_count

# 初始化 LINE Bot API 和處理器
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
# 從環境變數讀取提及關鍵字，並轉換為小寫列表
MENTION_KEYWORDS = os.getenv("MENTION_KEYWORDS", "@Test Local").lower().split(",")

def get_sender_id(event) -> str:
    """取得訊息發送者的 ID
    
    根據訊息來源類型（個人、群組、聊天室）返回對應的 ID
    
    Args:
        event: LINE 事件物件
    
    Returns:
        str: 發送者 ID
    """
    source = event.source
    if source.type == 'user':
        return source.user_id
    elif source.type == 'group':
        return source.group_id
    elif source.type == 'room':
        return source.room_id
    return "unknown"

def clean_markdown_for_line(text: str) -> str:
    """清理 Markdown 格式，使其適合在 LINE 中顯示
    
    Args:
        text (str): 包含 Markdown 格式的文字
    
    Returns:
        str: 清理後的文字
    """
    # 將 * 開頭的列表項目轉換為 • 
    text = re.sub(r'^\* ', '• ', text, flags=re.MULTILINE)
    # 移除粗體標記
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    # 移除斜體標記
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    # 移除其他 * 符號
    text = text.replace("*", "")
    return text.strip()

def remove_repetitive_messages(messages: list) -> list:
    """移除重複的使用者訊息
    
    Args:
        messages (list): 訊息歷史列表
    
    Returns:
        list: 清理後的訊息列表
    """
    cleaned = []
    prev = None
    for m in messages:
        if m["role"] == "user" and m["content"] == prev:
            continue
        cleaned.append(m)
        prev = m["content"] if m["role"] == "user" else None
    return cleaned

def handle_events(handler: WebhookHandler):
    """註冊 LINE Bot 事件處理器
    
    Args:
        handler (WebhookHandler): LINE Bot 的 webhook 處理器
    """
    @handler.add(MessageEvent, message=TextMessage)
    def handle_message(event):
        """處理文字訊息事件
        
        Args:
            event: LINE 訊息事件物件
        """
        # 取得發送者 ID 和訊息內容
        sender_id = get_sender_id(event)
        user_input = event.message.text.strip()
        
        # 處理清除歷史指令
        if user_input.lower() == "#清除":
            clear_history(sender_id)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="🔄 已清除你的對話歷史。")
            )
            return
            

        # 儲存使用者輸入到資料庫
        save_message(sender_id, "user", user_input)

        # 準備對話歷史，加入系統提示
        message = [{"role": "system", "content": "你是個樂於助人的繁體中文AI智能客服。請用富有人情味的語氣回答問題，並且保持簡潔，可以適當的加入emoji。如果不知道答案，請誠實地告訴使用者。"}]
        message += get_history(sender_id)
        # 移除重複訊息
        message = remove_repetitive_messages(message)

        # 呼叫 AI 模型生成回應
        reply = query_gemini(message)
        # 清理回應中的 Markdown 格式
        reply = clean_markdown_for_line(reply)

        # 儲存 AI 回應到資料庫
        save_message(sender_id, "assistant", reply)

        # 回覆訊息給使用者
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply)
        )