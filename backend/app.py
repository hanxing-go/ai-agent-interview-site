#!/usr/bin/env python3
"""
AI Agent 面经背诵助手 - 后端 API
Flask + SQLite，支持按专题每天刷 5 道题，勾选完成自动推进
"""

import sqlite3
import json
import os
from datetime import datetime, date
from flask import Flask, jsonify, request, g, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mianjing.db")
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")  # ai-agent-interview/


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
    return g.db


@app.teardown_appcontext
def close_db(e):
    db = g.pop("db", None)
    if db:
        db.close()


def init_db():
    """初始化数据库表"""
    db = sqlite3.connect(DB_PATH)
    db.execute("PRAGMA journal_mode=WAL")
    db.executescript("""
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            english TEXT,
            sort_order INTEGER DEFAULT 0,
            icon TEXT DEFAULT '📚'
        );

        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            novice_answer TEXT,
            expert_answer TEXT,
            companies TEXT,
            level TEXT DEFAULT 'medium',
            hot INTEGER DEFAULT 0,
            sort_order INTEGER DEFAULT 0,
            FOREIGN KEY (topic_id) REFERENCES topics(id)
        );

        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER UNIQUE NOT NULL,
            status TEXT DEFAULT 'pending',
            learned_at TEXT,
            review_count INTEGER DEFAULT 0,
            FOREIGN KEY (question_id) REFERENCES questions(id)
        );

        CREATE TABLE IF NOT EXISTS daily_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            topic_id INTEGER NOT NULL,
            question_ids TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        );

        CREATE INDEX IF NOT EXISTS idx_progress_status ON progress(status);
        CREATE INDEX IF NOT EXISTS idx_questions_topic ON questions(topic_id);
    """)
    db.commit()
    db.close()


# ─── API: 专题列表（含进度） ───

@app.route("/api/topics")
def get_topics():
    db = get_db()
    topics = db.execute(
        "SELECT t.*, "
        "(SELECT COUNT(*) FROM questions WHERE topic_id = t.id) as total, "
        "(SELECT COUNT(*) FROM questions q INNER JOIN progress p ON q.id = p.question_id "
        "WHERE q.topic_id = t.id AND p.status = 'learned') as learned "
        "FROM topics t ORDER BY t.sort_order"
    ).fetchall()

    result = []
    for t in topics:
        total = t["total"]
        learned = t["learned"]
        result.append({
            "id": t["id"],
            "name": t["name"],
            "english": t["english"],
            "icon": t["icon"],
            "sort_order": t["sort_order"],
            "total": total,
            "learned": learned,
            "progress_pct": round(learned / total * 100) if total > 0 else 0,
            "completed": total > 0 and learned >= total
        })
    return jsonify(result)


# ─── API: 获取今日 5 道题 ───

@app.route("/api/daily")
def get_daily():
    """获取今日要背的 5 道题，优先当前专题"""
    db = get_db()
    today = date.today().isoformat()

    # 检查今天是否已生成题目
    existing = db.execute(
        "SELECT * FROM daily_log WHERE date = ?", (today,)
    ).fetchone()

    if existing:
        qids = json.loads(existing["question_ids"])
        return _format_questions(db, qids, existing["topic_id"])

    # 找到当前活跃专题（第一个未完成的）
    current_topic = _get_current_topic(db)

    # 从当前专题取 5 道未学过的题
    unlearned = db.execute(
        "SELECT q.id FROM questions q "
        "LEFT JOIN progress p ON q.id = p.question_id AND p.status = 'learned' "
        "WHERE q.topic_id = ? AND p.id IS NULL "
        "ORDER BY q.sort_order LIMIT 5",
        (current_topic["id"],)
    ).fetchall()

    if not unlearned:
        return jsonify({
            "empty": True,
            "message": f"🎉 专题「{current_topic['name']}」全部学完！",
            "next_topic": _get_next_topic(db, current_topic["id"])
        })

    qids = [r["id"] for r in unlearned]

    # 记录今日题目
    db.execute(
        "INSERT INTO daily_log (date, topic_id, question_ids) VALUES (?, ?, ?)",
        (today, current_topic["id"], json.dumps(qids))
    )
    db.commit()

    return _format_questions(db, qids, current_topic["id"])


# ─── API: 切换专题后手动获取题目 ───

@app.route("/api/topics/<int:topic_id>/questions")
def get_topic_questions(topic_id):
    """获取指定专题的未学题目（最多5道）"""
    db = get_db()
    limit = request.args.get("limit", 5, type=int)

    unlearned = db.execute(
        "SELECT q.id FROM questions q "
        "LEFT JOIN progress p ON q.id = p.question_id AND p.status = 'learned' "
        "WHERE q.topic_id = ? AND p.id IS NULL "
        "ORDER BY q.sort_order LIMIT ?",
        (topic_id, limit)
    ).fetchall()

    if not unlearned:
        return jsonify({"empty": True, "message": "本专题全部学完！🎉"})

    qids = [r["id"] for r in unlearned]

    # 同时更新今日日志
    today = date.today().isoformat()
    db.execute(
        "INSERT OR REPLACE INTO daily_log (date, topic_id, question_ids) VALUES (?, ?, ?)",
        (today, topic_id, json.dumps(qids))
    )
    db.commit()

    return _format_questions(db, qids, topic_id)




# ─── API: 题库搜索 / 筛选 ───

@app.route("/api/questions")
def search_questions():
    """Search and filter questions.

    Query params:
    - keyword: search in question, answers, companies, topic name
    - topic_id: filter by topic id
    - difficulty: easy/basic/medium/hard/system-design/project
    - hot: true/1 to only show high-frequency questions
    - status: learned|pending|unlearned
    - limit / offset: pagination
    """
    db = get_db()
    keyword = (request.args.get("keyword") or "").strip()
    topic_id = request.args.get("topic_id", type=int)
    difficulty = (request.args.get("difficulty") or "").strip()
    hot = (request.args.get("hot") or "").lower() in {"1", "true", "yes", "on"}
    status = (request.args.get("status") or "").strip()
    limit = min(max(request.args.get("limit", 100, type=int), 1), 500)
    offset = max(request.args.get("offset", 0, type=int), 0)

    where = []
    params = []

    if topic_id:
        where.append("q.topic_id = ?")
        params.append(topic_id)
    if difficulty:
        where.append("q.level = ?")
        params.append(difficulty)
    if hot:
        where.append("q.hot > 0")
    if status in {"learned", "pending", "unlearned"}:
        if status == "learned":
            where.append("p.status = 'learned'")
        else:
            where.append("(p.status IS NULL OR p.status != 'learned')")
    if keyword:
        like = f"%{keyword}%"
        where.append("(q.question_text LIKE ? OR q.novice_answer LIKE ? OR q.expert_answer LIKE ? OR q.companies LIKE ? OR t.name LIKE ? OR t.english LIKE ?)")
        params.extend([like, like, like, like, like, like])

    where_sql = "WHERE " + " AND ".join(where) if where else ""
    total = db.execute(
        f"""
        SELECT COUNT(*) as c
        FROM questions q
        JOIN topics t ON q.topic_id = t.id
        LEFT JOIN progress p ON q.id = p.question_id
        {where_sql}
        """,
        params,
    ).fetchone()["c"]

    rows = db.execute(
        f"""
        SELECT q.*, t.name as topic_name, t.icon as topic_icon, t.english as topic_english,
               COALESCE(p.status, 'pending') as status, p.learned_at, p.review_count
        FROM questions q
        JOIN topics t ON q.topic_id = t.id
        LEFT JOIN progress p ON q.id = p.question_id
        {where_sql}
        ORDER BY q.hot DESC, t.sort_order ASC, q.sort_order ASC, q.id ASC
        LIMIT ? OFFSET ?
        """,
        params + [limit, offset],
    ).fetchall()

    questions = [_question_to_dict(r) for r in rows]
    return jsonify({
        "total": total,
        "limit": limit,
        "offset": offset,
        "questions": questions,
    })


# ─── API: 标记题目状态 ───

@app.route("/api/progress", methods=["POST"])
def update_progress():
    """标记题目为已学 / 待学"""
    data = request.get_json()
    question_id = data["question_id"]
    status = data.get("status", "learned")

    db = get_db()
    db.execute(
        "INSERT INTO progress (question_id, status, learned_at) VALUES (?, ?, ?) "
        "ON CONFLICT(question_id) DO UPDATE SET status = ?, learned_at = ?, review_count = review_count + 1",
        (question_id, status, datetime.now().isoformat() if status == "learned" else None,
         status, datetime.now().isoformat() if status == "learned" else None)
    )
    db.commit()
    return jsonify({"ok": True})


# ─── API: 重置专题进度 ───

@app.route("/api/topics/<int:topic_id>/reset", methods=["POST"])
def reset_topic(topic_id):
    """重置某个专题所有题目的学习状态"""
    db = get_db()
    db.execute(
        "DELETE FROM progress WHERE question_id IN "
        "(SELECT id FROM questions WHERE topic_id = ?)",
        (topic_id,)
    )
    db.commit()
    return jsonify({"ok": True})


# ─── API: 全局统计 ───

@app.route("/api/stats")
def get_stats():
    db = get_db()
    total = db.execute("SELECT COUNT(*) as c FROM questions").fetchone()["c"]
    learned = db.execute(
        "SELECT COUNT(*) as c FROM progress WHERE status = 'learned'"
    ).fetchone()["c"]
    today_q = db.execute(
        "SELECT COUNT(DISTINCT question_id) as c FROM progress WHERE date(learned_at) = date('now', 'localtime')"
    ).fetchone()["c"]

    return jsonify({
        "total_questions": total,
        "total_learned": learned,
        "today_learned": today_q,
        "progress_pct": round(learned / total * 100) if total > 0 else 0
    })


# ─── 辅助函数 ───

def _get_current_topic(db):
    """找到第一个未完成的专题"""
    topics = db.execute(
        "SELECT t.id, t.name, "
        "(SELECT COUNT(*) FROM questions WHERE topic_id = t.id) as total, "
        "(SELECT COUNT(*) FROM questions q INNER JOIN progress p ON q.id = p.question_id "
        "WHERE q.topic_id = t.id AND p.status = 'learned') as learned "
        "FROM topics t ORDER BY t.sort_order"
    ).fetchall()

    for t in topics:
        if t["learned"] < t["total"]:
            return {"id": t["id"], "name": t["name"]}
    # 全部学完
    return {"id": topics[0]["id"], "name": topics[0]["name"]}


def _get_next_topic(db, current_id):
    topics = db.execute(
        "SELECT t.id, t.name, "
        "(SELECT COUNT(*) FROM questions WHERE topic_id = t.id) as total, "
        "(SELECT COUNT(*) FROM questions q INNER JOIN progress p ON q.id = p.question_id "
        "WHERE q.topic_id = t.id AND p.status = 'learned') as learned "
        "FROM topics t WHERE t.sort_order > (SELECT sort_order FROM topics WHERE id = ?) "
        "ORDER BY t.sort_order LIMIT 1",
        (current_id,)
    ).fetchone()
    if topics:
        return {"id": topics["id"], "name": topics["name"]}
    return None



def _question_to_dict(q):
    return {
        "id": q["id"],
        "topic_id": q["topic_id"],
        "topic_name": q["topic_name"] if "topic_name" in q.keys() else None,
        "topic_icon": q["topic_icon"] if "topic_icon" in q.keys() else None,
        "topic_english": q["topic_english"] if "topic_english" in q.keys() else None,
        "question_text": q["question_text"],
        "novice_answer": q["novice_answer"],
        "expert_answer": q["expert_answer"],
        "companies": q["companies"].split(",") if q["companies"] else [],
        "level": q["level"],
        "hot": q["hot"],
        "status": q["status"] if "status" in q.keys() else "pending",
        "learned_at": q["learned_at"] if "learned_at" in q.keys() else None,
        "review_count": q["review_count"] if "review_count" in q.keys() else 0,
    }

def _format_questions(db, qids, topic_id):
    questions = []
    for qid in qids:
        q = db.execute("SELECT * FROM questions WHERE id = ?", (qid,)).fetchone()
        if q:
            questions.append({
                "id": q["id"],
                "topic_id": q["topic_id"],
                "question_text": q["question_text"],
                "novice_answer": q["novice_answer"],
                "expert_answer": q["expert_answer"],
                "companies": q["companies"].split(",") if q["companies"] else [],
                "level": q["level"],
                "hot": q["hot"]
            })

    topic = db.execute("SELECT * FROM topics WHERE id = ?", (topic_id,)).fetchone()
    learned_count = db.execute(
        "SELECT COUNT(*) as c FROM questions q "
        "INNER JOIN progress p ON q.id = p.question_id "
        "WHERE q.topic_id = ? AND p.status = 'learned'",
        (topic_id,)
    ).fetchone()["c"]
    total_count = db.execute(
        "SELECT COUNT(*) as c FROM questions WHERE topic_id = ?", (topic_id,)
    ).fetchone()["c"]

    return jsonify({
        "topic": {"id": topic["id"], "name": topic["name"], "icon": topic["icon"]},
        "progress": {"learned": learned_count, "total": total_count},
        "questions": questions
    })


# ─── 静态文件 ───

@app.route("/")
def serve_index():
    return send_from_directory(STATIC_DIR, "index.html")

@app.route("/study")
def serve_study():
    return send_from_directory(STATIC_DIR, "study.html")

@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(STATIC_DIR, filename)


# ─── 启动 ───

if __name__ == "__main__":
    init_db()
    print("🎵 小Miku的面经背诵助手已启动！ http://0.0.0.0:5001")
    app.run(host="0.0.0.0", port=5001, debug=False)
