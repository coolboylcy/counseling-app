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

请使用 Markdown 格式生成总结报告，包含以下部分：

# 文档概述
简要介绍文档的主要内容和目的。

## 核心要点
列出文档中最重要和关键的信息点。

### 技术细节
- 重要的技术概念和实现细节
- 关键的技术参数和配置
- 核心功能说明

### 创新亮点
- 文档中的创新点
- 独特的解决方案
- 重要的突破

## 总结
对文档进行整体评价和总结。

注意：
1. 使用 Markdown 的标题层级（#、##、###）来组织内容
2. 使用列表（- 或 1.）来列举要点
3. 使用引用（>）来突出重要内容
4. 使用代码块（```）来展示代码示例
5. 保持客观专业的语气
6. 确保内容简洁明了，重点突出

请以专业秘书的身份为用户提供文档总结。"""

# 类比解析的系统提示词
ANALOGY_PROMPT = """你是一位擅长用类比方法解释复杂技术概念的教育专家。
你的任务是用生动有趣的类比来帮助用户理解技术文档中的概念。

请按照以下步骤生成类比解析：

1. 首先识别文档中的核心概念和技术难点
2. 为每个核心概念找到合适的类比对象
3. 使用循序渐进的方式，从简单到复杂地解释
4. 确保类比贴近日常生活，易于理解
5. 在解释过程中适当使用比喻和类比

输出格式要求：
1. 使用 Markdown 格式
2. 每个概念使用独立的类比段落
3. 使用引用块来突出重要的类比说明
4. 适当使用表情符号增加趣味性
5. 保持专业性的同时确保通俗易懂

请以教育专家的身份，用生动的类比帮助用户理解文档内容。"""

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
    is_premium = data.get('premium', False)
    
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
        
        # 根据是否是高级解析选择不同的提示词
        system_prompt = ANALOGY_PROMPT if is_premium else SYSTEM_PROMPT
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"请分析以下文档内容，并{'用类比方法深入解析' if is_premium else '生成一份专业的总结报告'}：\n\n{document_content}"}
            ]
        }
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        response_data = {
            "document_type": "PDF" if document_url.lower().endswith('.pdf') else 
                           "Markdown" if document_url.lower().endswith('.md') else 
                           "HTML" if document_url.lower().endswith('.html') else "Text"
        }
        
        if is_premium:
            response_data["analogy"] = result['choices'][0]['message']['content']
        else:
            response_data["summary"] = result['choices'][0]['message']['content']
        
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 