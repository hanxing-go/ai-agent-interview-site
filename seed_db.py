#!/usr/bin/env python3
"""
Seed SQLite database from structured JSON data.

This script loads:
- data/topics.json
- data/questions/*.json

By default it rebuilds topics/questions and clears progress/daily logs, matching
the old behavior. Keep production DB backups before running on a live server.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
DATA_DIR = ROOT / "data"
QUESTIONS_DIR = DATA_DIR / "questions"
DB_PATH = BACKEND_DIR / "mianjing.db"

VALID_DIFFICULTIES = {"easy", "basic", "medium", "hard", "system-design", "project"}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_companies(value):
    if value is None:
        return ""
    if isinstance(value, list):
        return ",".join(str(v).strip() for v in value if str(v).strip())
    return str(value)


def validate_topics(topics: list[dict]) -> None:
    ids = set()
    slugs = set()
    for topic in topics:
        for field in ["id", "slug", "name", "english", "icon"]:
            if field not in topic:
                raise ValueError(f"topic missing field {field}: {topic}")
        if topic["id"] in ids:
            raise ValueError(f"duplicate topic id: {topic['id']}")
        if topic["slug"] in slugs:
            raise ValueError(f"duplicate topic slug: {topic['slug']}")
        ids.add(topic["id"])
        slugs.add(topic["slug"])


def load_questions(topic_ids: set[int]) -> list[dict]:
    questions: list[dict] = []
    seen_ids: set[str] = set()
    for path in sorted(QUESTIONS_DIR.glob("*.json")):
        items = load_json(path)
        if not isinstance(items, list):
            raise ValueError(f"{path} must contain a JSON array")
        for index, q in enumerate(items, start=1):
            for field in ["id", "topic_id", "question", "difficulty", "novice_answer", "expert_answer"]:
                if field not in q:
                    raise ValueError(f"{path}:{index} missing field {field}")
            if q["id"] in seen_ids:
                raise ValueError(f"duplicate question id: {q['id']}")
            if q["topic_id"] not in topic_ids:
                raise ValueError(f"{q['id']} references unknown topic_id {q['topic_id']}")
            if q["difficulty"] not in VALID_DIFFICULTIES:
                raise ValueError(f"{q['id']} invalid difficulty: {q['difficulty']}")
            if not str(q["question"]).strip():
                raise ValueError(f"{q['id']} question is empty")
            if not str(q["expert_answer"]).strip():
                raise ValueError(f"{q['id']} expert_answer is empty")
            q.setdefault("hot", 0)
            q.setdefault("sort_order", index)
            q.setdefault("companies", [])
            q.setdefault("tags", [])
            seen_ids.add(q["id"])
            questions.append(q)
    return questions


def init_schema(db_path: Path = DB_PATH) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(db_path)
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


def seed(db_path: Path = DB_PATH) -> None:
    init_schema(db_path)
    topics = load_json(DATA_DIR / "topics.json")
    validate_topics(topics)
    questions = load_questions({int(t["id"]) for t in topics})

    db = sqlite3.connect(db_path)
    db.execute("PRAGMA journal_mode=WAL")

    for table in ["daily_log", "progress", "questions", "topics"]:
        db.execute(f"DELETE FROM {table}")
    db.execute("DELETE FROM sqlite_sequence WHERE name IN ('topics','questions','progress','daily_log')")

    for topic in sorted(topics, key=lambda t: t.get("sort_order", t["id"])):
        db.execute(
            "INSERT INTO topics (id, name, english, sort_order, icon) VALUES (?,?,?,?,?)",
            (
                int(topic["id"]),
                topic["name"],
                topic.get("english", ""),
                int(topic.get("sort_order", topic["id"])),
                topic.get("icon", "📚"),
            ),
        )

    for q in sorted(questions, key=lambda item: (int(item["topic_id"]), int(item.get("sort_order", 0)))):
        db.execute(
            """
            INSERT INTO questions
            (topic_id, question_text, novice_answer, expert_answer, companies, level, hot, sort_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                int(q["topic_id"]),
                q["question"],
                q.get("novice_answer", ""),
                q.get("expert_answer", ""),
                normalize_companies(q.get("companies")),
                q.get("difficulty", "medium"),
                int(q.get("hot", 0)),
                int(q.get("sort_order", 0)),
            ),
        )

    db.commit()
    db.close()
    print(f"✅ Seeded {len(topics)} topics and {len(questions)} questions into {db_path}")


if __name__ == "__main__":
    seed()
