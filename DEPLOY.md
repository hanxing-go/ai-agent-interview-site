# Deployment Guide

当前项目已经可以部署在公网服务器上。建议线上部署和 GitHub 协作分离：GitHub 存代码，服务器保留数据库和运行时数据。

## 1. Clone / Pull

```bash
git clone https://github.com/hanxing-go/ai-agent-interview-site.git
cd ai-agent-interview-site
```

或线上已有目录：

```bash
git pull origin main
```

## 2. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 3. Initialize Database

```bash
python seed_db.py
```

生产环境已有 `backend/mianjing.db` 时，不要覆盖；先备份：

```bash
cp backend/mianjing.db backend/mianjing.db.bak.$(date +%Y%m%d-%H%M%S)
```

## 4. Run Backend

```bash
source venv/bin/activate
python backend/app.py
```

建议后续改成 systemd/supervisor 管理。

## 5. Daily Crawl

```bash
WORKDIR=/path/to/ai-agent-interview-site \
PUBLIC_HTML_DIR=/path/to/public_html/interview \
bash crawl.sh
```

Cron 示例：

```cron
0 9 * * * cd /path/to/ai-agent-interview-site && WORKDIR=$PWD PUBLIC_HTML_DIR=/path/to/public_html/interview bash crawl.sh
```

## 6. Collaboration Safety

不要提交：

- SQLite 生产数据库
- 日志
- `.env`
- 抓取生成的 raw/new 快照
- 服务器私有路径或密钥
