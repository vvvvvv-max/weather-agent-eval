import os
import json
import re
import requests
from dotenv import load_dotenv
from openai import OpenAI

# 1. 載入環境變數
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("DASHSCOPE_BASE_URL")
qweather_key = os.getenv("QWEATHER_API_KEY")

if not api_key or not qweather_key:
    print("錯誤：請確認 .env 檔案中有 OPENAI_API_KEY 和 QWEATHER_API_KEY")
    exit()

client = OpenAI(api_key=api_key, base_url=base_url)

# 2. 定義 Prompts
L1_PROMPT = """你是一個天氣查詢助手。你有兩個工具可用：
1. weather(city): 查詢單個城市天氣。
2. multi_weather(cities): 查詢多個城市天氣。
請使用 ReAct 模式進行思考。你必須輸出嚴格的 JSON 格式，包含 "thought", "action", "action_input" 三個欄位。"""

L2_PROMPT = """你是一個天氣查詢助手。你有兩個工具可用：
1. weather(city): 查詢單個城市天氣。
2. multi_weather(cities): 查詢多個城市天氣。
請仔細閱讀以下標準互動範例，學習其格式和思考邏輯：
【範例 1】輸入: 湛江麻章區現在的天氣怎麼樣？ 輸出: {"thought": "用戶詢問湛江麻章區的天氣，我應該呼叫 weather 工具。", "action": "weather", "action_input": {"city": "湛江麻章"}}
【範例 2】輸入: 幫我查一下湛江麻章和赤坎這兩個區的天氣。 輸出: {"thought": "用戶一次性詢問了兩個地區的天氣，我應該使用 multi_weather 工具進行並行查詢。", "action": "multi_weather", "action_input": {"cities": ["湛江麻章", "湛江赤坎"]}}
請嚴格按照上述範例的 JSON 格式輸出。"""

def call_llm(system_prompt, user_input):
    try:
        response = client.chat.completions.create(
            model="deepseek-v4-flash-0731",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_input}],
            temperature=0.0
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"呼叫 API 失敗: {str(e)}"

def get_real_weather(city_name):
    try:
        api_host = "p94nmwefay.re.qweatherapi.com"
        city_coords = {"湛江麻章": "110.33,21.26", "湛江赤坎": "110.36,21.27", "湛江霞山": "110.41,21.19"}
        
        if city_name in city_coords:
            location = city_coords[city_name]
        else:
            return {"error": f"找不到城市 {city_name}"}
            
        weather_url = f"https://{api_host}/v7/weather/now?location={location}&key={qweather_key}"
        weather_res = requests.get(weather_url)
        
        if weather_res.status_code != 200:
            return {"error": f"API 請求失敗 (HTTP {weather_res.status_code})"}

        weather_data = weather_res.json()
        if weather_data.get("code") == "200":
            now = weather_data["now"]
            return {"city": city_name, "temp": now["temp"] + "°C", "weather": now["text"]}
        else:
            return {"error": "查詢天氣失敗"}
    except Exception as e:
        return {"error": f"程式異常: {str(e)}"}

if __name__ == "__main__":
    query = "幫我查一下湛江麻章和赤坎這兩個區現在的氣溫和天氣。"
    print(f"【測試問題】: {query}\n")
    
    print("--- 實驗 A (L1 基礎提示) 輸出 ---")
    output_L1 = call_llm(L1_PROMPT, query)
    print(output_L1)
    print("\n")
    
    print("--- 實驗 B (L2 注入範例) 輸出 ---")
    output_L2 = call_llm(L2_PROMPT, query)
    print(output_L2)
    print("\n" + "="*60 + "\n")

    print("--- 開始執行真實 Agent 工具調用 ---")
    try:
        json_match = re.search(r'\{.*\}', output_L2, re.DOTALL)
        if json_match:
            action_data = json.loads(json_match.group(0))
            action = action_data.get("action")
            action_input = action_data.get("action_input", {})
            
            print(f"[系統動作] 正在呼叫和風天氣真實 API，工具: {action}...")
            
            if action == "multi_weather":
                cities = action_input.get("cities", [])
                results = [get_real_weather(c) for c in cities]
                observation = json.dumps(results, ensure_ascii=False)
            elif action == "weather":
                city = action_input.get("city", "")
                observation = json.dumps(get_real_weather(city), ensure_ascii=False)
            else:
                observation = json.dumps({"error": "未知的工具"})
                
            print(f"[氣象局回傳] {observation}\n")
            
            print("--- 最終回答 (Final Answer) ---")
            final_prompt = f"用戶問：{query}\n工具查到的真實數據：{observation}\n請根據真實數據，用自然語言回答用戶。"
            final_answer = call_llm("你是一個天氣助手，請根據工具結果回答問題。", final_prompt)
            print(final_answer)
            print("\n" + "="*60 + "\n")
            
    except Exception as e:
        print(f"[執行失敗] {e}")