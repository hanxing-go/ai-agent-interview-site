# AI Agent Interview Site

> 面向 AI Agent / RAG / LLM 应用开发方向的开源面试题库、刷题工具与共建社区。

AI Agent Interview Site 希望把零散的真实面经、Agent 工程实践题、RAG 高频追问、MCP / Tool Calling / Memory 等知识点，整理成一个可搜索、可刷题、可共建的中文面试知识库。

如果你正在准备 **AI Agent 工程师、LLM 应用开发、AI 后端、RAG 工程、MCP / 工具调用相关岗位**，这个项目就是为你准备的。

---

## Why This Project?

AI Agent 方向的面试题正在快速变化：

- 只会背 “Agent 是什么” 已经不够了；
- 面试官越来越喜欢追问工程细节：工具失败怎么办？RAG 怎么评估？Memory 怎么设计？成本怎么控制？
- 大量面经分散在牛客、博客、群聊和个人笔记里，不容易系统复习；
- 很多答案停留在概念层，不能直接用于面试表达。

所以这个项目想做三件事：

1. **收集真实高频题**：沉淀 AI Agent / RAG / LLM 应用开发方向的面试题。
2. **整理可表达答案**：每道题尽量给出新手版、专业版、易错点和追问方向。
3. **建立共建流程**：让更多同学可以通过 Issue / PR 投稿题目、面经和项目经验。

---

## What You Can Do Here

- 📚 按专题学习 AI Agent 高频面试题
- 🎯 每天刷 5 道题，持续积累
- ✅ 记录学习进度
- 🔁 按专题切换、重置、复习
- 🧠 对比新手版回答和专业版回答
- 🧩 整理真实面经、公司追问和项目深挖题
- 🤝 通过 GitHub Issue / PR 参与共建

---

## Topic Coverage

当前和计划覆盖的专题包括：

| 专题 | 内容 |
|------|------|
| Agent 基础 | Agent vs Workflow、ReAct、Planner、Executor |
| Tool Calling | Function Calling、工具注册、参数校验、错误恢复 |
| MCP / A2A | 协议设计、工具发现、上下文传输、生态差异 |
| RAG | 检索、分块、Embedding、重排、幻觉缓解、评估 |
| Memory | 短期记忆、长期记忆、用户画像、记忆压缩 |
| Multi-Agent | 多智能体协作、任务拆解、冲突处理 |
| 工程化 | 部署、监控、成本控制、延迟优化、稳定性 |
| 项目深挖 | 简历项目、Agent 项目复盘、面试官追问 |
| 真实面经 | 公司、岗位、轮次、题目和复盘 |

详见 [Roadmap](docs/roadmap.md)。

---

## Screens / Pages

当前项目包含两个主要页面：

- `index.html`：面经信息 / 首页
- `study.html`：刷题学习页

后端使用 Flask + SQLite，提供专题、每日题目、进度记录等 API。

---

## Project Structure

```text
.
├── index.html                       # 首页 / 面经信息页
├── study.html                       # 刷题学习页
├── backend/
│   └── app.py                       # Flask API + SQLite
├── seed_db.py                       # 初始化题库数据
├── crawl.sh                         # 每日抓取公开面经链接摘要
├── data/
│   ├── topics.json                  # 专题元数据
│   ├── questions/                   # 结构化题库 JSON
│   └── zero2agent-topics.json       # 专题数据示例
├── scripts/
│   └── validate_questions.py        # 题库数据校验
├── docs/
│   ├── roadmap.md                   # 项目路线图
│   └── content-standard.md          # 内容标准
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── question.yml             # 面试题投稿模板
│   │   └── interview-experience.yml # 真实面经投稿模板
│   └── pull_request_template.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── DEPLOY.md
├── requirements.txt
└── .env.example
```

---

## Quick Start

### 1. Clone

```bash
git clone https://github.com/hanxing-go/ai-agent-interview-site.git
cd ai-agent-interview-site
```

### 2. Install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Validate question data

```bash
python scripts/validate_questions.py
```

### 4. Initialize database

```bash
python seed_db.py
```

### 5. Start backend

```bash
python backend/app.py
```

默认后端端口：

```text
http://127.0.0.1:5001
```

### 6. Open pages

你可以直接打开：

```text
index.html
study.html
```

或根据部署方式通过 Web Server / Flask 静态服务访问。

---

## API Overview

当前 Flask 后端提供：

| API | 说明 |
|-----|------|
| `GET /api/topics` | 获取专题列表和学习进度 |
| `GET /api/daily` | 获取今日 5 道题 |
| `GET /api/topics/<id>/questions` | 获取指定专题题目 |
| `POST /api/progress` | 标记题目学习状态 |
| `POST /api/topics/<id>/reset` | 重置专题进度 |
| `GET /api/stats` | 获取全局统计 |

---

## Question Data

题库已经拆成结构化 JSON，方便朋友和开源贡献者直接补题：

```text
data/topics.json
data/questions/*.json
```

新增或修改题目后，请先运行：

```bash
python scripts/validate_questions.py
python seed_db.py
```

每道题的字段规范见 [docs/content-standard.md](docs/content-standard.md)。

## Data and Runtime Files

仓库不会提交运行时文件：

```text
backend/mianjing.db
*.log
venv/
__pycache__/
data/raw-*.txt
data/new-*.txt
.env
```

如果你在本地或服务器运行项目，请注意不要把数据库、日志、密钥和抓取快照提交到仓库。

---

## How to Contribute

我们欢迎三类贡献：

### 1. 投稿面试题

适合想补充单道题目的同学。

请使用 Issue 模板：**面试题投稿**。

建议包含：

- 题目
- 所属专题
- 难度
- 新手版回答
- 专业版回答
- 考察点
- 易错点
- 面试官追问
- 来源 / 公司（可匿名）

### 2. 投稿真实面经

适合刚参加完面试的同学。

请使用 Issue 模板：**真实面经投稿**。

请注意脱敏，不要泄露个人隐私、面试官信息或公司内部资料。

### 3. 提交代码改进

适合开发贡献者。

建议流程：

```text
Fork 仓库
→ 创建分支
→ 修改代码 / 文档 / 题库
→ 提交 Pull Request
→ 维护者 Review
→ 合并
```

贡献前请阅读：

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [docs/content-standard.md](docs/content-standard.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

---

## Content Standard

我们希望题目不是简单堆积，而是能真正帮助面试表达。

一条高质量题目最好包含：

```text
题目
所属专题
难度
标签
新手版回答
专业版回答
考察点
易错点
可能追问
参考来源
```

示例：

```text
题目：RAG 如何缓解大模型幻觉？
结论：RAG 不能彻底消除幻觉，但可以显著降低事实性错误。
展开：通过检索外部知识、引用来源、重排过滤、拒答机制和评估集持续优化。
易错点：不要说 RAG 是万能方案，检索质量差时仍然会幻觉。
追问：如何评估 RAG？RAG 和微调怎么取舍？
```

完整标准见 [docs/content-standard.md](docs/content-standard.md)。

---

## Roadmap

近期重点：

- [x] 开源仓库基础设施
- [x] Issue / PR 模板
- [x] 内容标准文档
- [x] 题库 JSON 化
- [ ] 搜索和标签筛选
- [ ] 高频题榜单
- [ ] 收藏 / 错题本
- [ ] 模拟面试模式
- [ ] GitHub Actions 自动部署
- [ ] 贡献者榜单

完整路线图见 [docs/roadmap.md](docs/roadmap.md)。

---

## Deployment

部署说明见 [DEPLOY.md](DEPLOY.md)。

建议线上环境：

```text
GitHub 仓库存代码
服务器保留 SQLite 数据库和日志
合并 PR 后服务器拉取最新代码并重启服务
```

后续可以接入 GitHub Actions 自动部署。

---

## Community Vision

这个项目不是想做一个只有作者维护的小页面，而是希望逐步变成：

> **AI Agent 面试导航站 + 高频题库 + 模拟面试工具 + 真实面经共建社区。**

如果你也在准备 AI Agent / RAG / LLM 应用开发方向的面试，欢迎一起补题、修答案、写复盘、提功能建议。

哪怕只是补充一道你刚被问到的题，也可能帮到后面的很多人。

---

## License

[MIT](LICENSE)
