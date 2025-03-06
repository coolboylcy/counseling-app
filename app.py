from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv

app = Flask(__name__, static_folder='static')
load_dotenv()

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', "sk-b225609809eb45da981394d494dafe3d")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# 系统提示词，让AI扮演专业心理咨询师
SYSTEM_PROMPT = """你是一位经验丰富的心理咨询师，拥有超过15年的临床经验。你擅长倾听、共情，并能够提供专业的心理支持和建议。
你的沟通风格温和、专业，善于运用认知行为疗法、正念疗法等专业方法。
在回答时，你会：
1. 保持专业性和同理心
2. 避免使用AI或机器相关的词汇
3. 根据来访者的具体情况提供个性化的建议
4. 在必要时建议寻求线下专业帮助
5. 保持适度的情感距离，避免过度承诺
请以专业心理咨询师的身份与来访者对话。"""

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
    }
    
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return jsonify({"response": result['choices'][0]['message']['content']})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 