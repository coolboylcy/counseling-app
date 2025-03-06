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
        
        # 模拟响应数据
        response_data = {
            "document_type": "PDF" if document_url.lower().endswith('.pdf') else 
                           "Markdown" if document_url.lower().endswith('.md') else 
                           "HTML" if document_url.lower().endswith('.html') else "Text"
        }
        
        if is_premium:
            response_data["analogy"] = """# 深入解析示例

## 核心概念类比

### 1. 文档处理系统
就像图书馆的管理系统一样，我们的文档分析系统：
- 接收各种格式的文档（就像图书馆接收不同语言的书籍）
- 提取关键信息（就像图书管理员整理书籍信息）
- 生成结构化摘要（就像制作图书目录）

### 2. 文本分析过程
这个过程可以类比为：
- 提取内容：就像厨师准备食材
- 理解核心：就像厨师理解菜谱
- 生成类比：就像厨师创新菜品
- 优化输出：就像摆盘和装饰

> 通过这样的类比，我们可以更好地理解文档分析系统的工作原理。"""
        else:
            response_data["summary"] = """# 文档分析示例

## 文档概述
这是一个示例文档分析结果，展示了系统的基本功能。

## 核心要点
- 支持多种文档格式
- 智能提取关键信息
- 生成结构化摘要

### 技术细节
- 文档格式识别
- 文本内容提取
- 信息结构化处理

### 创新亮点
- 智能分析算法
- 多格式支持
- 实时处理能力

## 总结
这是一个功能强大的文档分析系统，能够帮助用户快速理解和总结各类文档。"""
        
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 