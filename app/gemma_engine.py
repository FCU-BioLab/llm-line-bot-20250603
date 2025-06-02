#app/gemma_engine.py
import os
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_fixed

# === 初始化 Gemini 模型 ===
# 從環境變數讀取 API 金鑰
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# 設定 Gemini API 金鑰
genai.configure(api_key=GEMINI_API_KEY)

# 初始化 Gemini 模型
model_gemini = genai.GenerativeModel(
    model_name="gemma-3-27b-it",  # ✅ 目前可用的正式模型名稱
    # 設定生成參數
    generation_config={
        "temperature": 0.7,      # 控制回應的隨機性（0-1）
        "top_p": 1,             # 控制詞彙選擇的多樣性
        "top_k": 40,            # 控制每次選擇的候選詞數量
        "max_output_tokens": 2048,  # 最大輸出長度
    }
)

# === Gemini 查詢函數 ===
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))  # 失敗時最多重試 3 次，每次間隔 2 秒
def query_gemini(messages: list) -> str:
    """向 Gemini 模型發送查詢並取得回應
    
    將對話歷史轉換為文字格式後發送給模型，並處理回應結果
    
    Args:
        messages (list): 對話歷史列表，每則訊息包含 role 和 content
    
    Returns:
        str: 模型的回應文字，或在發生錯誤時返回錯誤訊息
    """
    # 將對話歷史轉換為純文字格式
    prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])

    try:
        # 呼叫 Gemini 模型生成回應
        response = model_gemini.generate_content(prompt)

        # 檢查回應是否包含文字內容
        if hasattr(response, "text"):
            result = response.text.strip()
            return result
        else:
            return "⚠️ Gemini 沒有回應內容，請稍後再試。"

    except Exception as e:
        # 記錄錯誤並返回友善的錯誤訊息
        print(f"❌ Gemini 發生錯誤：{e}")
        return f"發生錯誤，請稍後再試😉"