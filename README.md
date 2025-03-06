# 专业心理咨询系统

这是一个基于 DeepSeek API 的专业心理咨询系统，提供在线心理支持和指导。

## 功能特点

- 专业的心理咨询服务
- 友好的用户界面
- 实时对话支持
- 安全的数据传输

## 本地运行

1. 克隆项目
```bash
git clone [项目地址]
cd [项目目录]
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 运行应用
```bash
python app.py
```

4. 访问应用
打开浏览器访问 http://localhost:5000

## Docker 部署

1. 构建 Docker 镜像
```bash
docker build -t counseling-app .
```

2. 运行容器
```bash
docker run -d -p 5000:5000 counseling-app
```

3. 访问应用
打开浏览器访问 http://localhost:5000

## 注意事项

- 本系统仅供参考，如有严重心理问题请及时寻求线下专业帮助
- 请勿在对话中透露个人敏感信息
- 系统响应时间可能因网络状况而异

## 技术栈

- Python Flask
- DeepSeek API
- HTML/CSS/JavaScript
- Docker 