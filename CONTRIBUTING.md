# Contributing to AI Agent Interview Site

感谢你愿意一起建设 AI Agent 面经知识库！这个项目希望帮助更多同学系统准备 AI Agent / RAG / LLM 应用开发相关面试。

## 你可以贡献什么

### 1. 补充面试题

适合内容贡献者。请优先使用 GitHub Issue 模板：**面试题投稿**。

建议包含：

- 题目
- 所属专题
- 难度
- 新手版回答
- 专业版回答
- 考察点
- 易错点
- 面试官追问
- 来源/公司（可匿名）

### 2. 补充真实面经

适合刚面完或正在准备面试的同学。请使用 GitHub Issue 模板：**真实面经投稿**。

请尽量去除个人隐私和敏感信息。

### 3. 改进网站功能

适合开发贡献者。建议先开 Issue 讨论，再提交 Pull Request。

可做方向：

- 搜索 / 标签筛选
- 收藏 / 错题本
- 模拟面试模式
- 题库 JSON 化
- 移动端样式优化
- 自动部署

## 分支命名建议

```text
content/add-rag-questions
content/update-agent-answer
feat/search
fix/mobile-layout
docs/update-readme
```

## Commit Message 建议

```text
content: add RAG evaluation questions
feat: add topic filter
fix: correct MCP answer
/docs: update roadmap
```

## Pull Request 自查

提交 PR 前请确认：

- [ ] 没有提交 `backend/mianjing.db`
- [ ] 没有提交日志文件
- [ ] 没有提交 `.env` 或密钥
- [ ] 内容来源合规，可公开分享
- [ ] 新增题目符合 `docs/content-standard.md`
- [ ] 页面/接口改动已本地验证

## 本地运行

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python seed_db.py
python backend/app.py
```

## 内容原则

1. 面向真实面试，不堆概念。
2. 回答要能直接开口表达。
3. 标注易错点和追问方向。
4. 优先沉淀高频、工程化、项目深挖题。
5. 尊重原创和平台规则，不搬运大段受版权保护内容。
