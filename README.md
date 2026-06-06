# AI Agent Interview Site

AI Agent 面经背诵/学习网站，用于整理 AI Agent、RAG、MCP、工具调用、工程化等方向的面试题，并支持每日刷题与进度记录。

## Features

- 📚 专题化面经题库
- ✅ 学习进度记录
- 🎯 每日 5 题
- 🔁 按专题重置/切换
- 🌐 静态前端 + Flask API
- 🕘 可选每日抓取脚本，收集公开面经链接

## Project Structure

```text
.
├── index.html          # 面经信息/首页
├── study.html          # 刷题学习页
├── backend/
│   └── app.py          # Flask API + SQLite
├── seed_db.py          # 初始化题库数据
├── crawl.sh            # 每日抓取脚本
├── data/
│   └── zero2agent-topics.json
├── requirements.txt
└── .env.example
```

## Local Development

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python seed_db.py
python backend/app.py
```

默认后端端口：`5001`。

打开：

- `index.html`
- `study.html`

如果前端部署在同一目录，Flask 也会提供静态文件。

## Data and Runtime Files

仓库默认不提交以下运行时文件：

- `backend/mianjing.db`
- `*.log`
- `venv/`
- `__pycache__/`
- `data/raw-*.txt`
- `data/new-*.txt`

如需初始化数据库，请运行：

```bash
python seed_db.py
```

## Collaboration Workflow

建议协作方式：

1. 好友 fork 或创建分支
2. 修改题库/页面/后端逻辑
3. 提 Pull Request
4. 合并后在服务器拉取并重启服务

内容贡献可以先走 GitHub Issues：一条 issue 对应一个题目/专题/答案改进。

## Notes

本项目用于个人学习与面试准备。抓取脚本仅保存公开搜索结果链接摘要；请注意遵守目标网站条款与版权要求。
