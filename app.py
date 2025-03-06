from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv
import PyPDF2
import markdown
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse

app = Flask(__name__, static_folder='static')
load_dotenv()

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', "sk-b225609809eb45da981394d494dafe3d")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# 系统提示词，让AI扮演专业文档分析秘书
SYSTEM_PROMPT = """你是一位专业的文档分析秘书，擅长快速理解和总结各类技术文档。
你的工作风格清晰、专业，善于提取文档的核心内容和关键信息。
在总结时，你会：
1. 提取文档的主要观点和核心内容
2. 列出关键的技术要点和重要发现
3. 用通俗易懂的语言解释复杂概念
4. 突出文档的创新点和重要结论
5. 保持客观专业的语气
请以专业秘书的身份为用户提供文档总结。"""

def extract_text_from_pdf(pdf_content):
    pdf_reader = PyPDF2.PdfReader(pdf_content)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_markdown(markdown_content):
    html = markdown.markdown(markdown_content)
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()

def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text()

def fetch_document_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        content_type = response.headers.get('content-type', '').lower()
        
        if 'pdf' in content_type:
            return extract_text_from_pdf(response.content)
        elif 'markdown' in content_type or url.endswith('.md'):
            return extract_text_from_markdown(response.text)
        elif 'html' in content_type:
            return extract_text_from_html(response.text)
        else:
            return response.text
    except Exception as e:
        return f"Error fetching document: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    document_url = data.get('url', '')
    
    if not document_url:
        return jsonify({"error": "请提供文档链接"}), 400
    
    try:
        # 获取文档内容
        document_content = fetch_document_content(document_url)
        
        # 准备发送给 AI 的消息
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"请分析以下文档内容，并生成一份专业的总结报告：\n\n{document_content}"}
            ]
        }
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        return jsonify({
            "summary": result['choices'][0]['message']['content'],
            "document_type": "PDF" if document_url.lower().endswith('.pdf') else 
                           "Markdown" if document_url.lower().endswith('.md') else 
                           "HTML" if document_url.lower().endswith('.html') else "Text"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 