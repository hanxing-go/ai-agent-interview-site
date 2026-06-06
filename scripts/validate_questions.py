#!/usr/bin/env python3
"""Validate structured question data for contributors and CI."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
QUESTIONS_DIR = DATA_DIR / "questions"
VALID_DIFFICULTIES = {"easy", "basic", "medium", "hard", "system-design", "project"}


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"❌ Invalid JSON: {path}: {exc}") from exc


def main() -> int:
    topics = load(DATA_DIR / "topics.json")
    topic_ids = set()
    topic_slugs = set()
    for topic in topics:
        for field in ["id", "slug", "name", "english", "icon"]:
            if field not in topic:
                raise SystemExit(f"❌ Topic missing {field}: {topic}")
        if topic["id"] in topic_ids:
            raise SystemExit(f"❌ Duplicate topic id: {topic['id']}")
        if topic["slug"] in topic_slugs:
            raise SystemExit(f"❌ Duplicate topic slug: {topic['slug']}")
        topic_ids.add(topic["id"])
        topic_slugs.add(topic["slug"])

    seen = set()
    total = 0
    for path in sorted(QUESTIONS_DIR.glob("*.json")):
        items = load(path)
        if not isinstance(items, list):
            raise SystemExit(f"❌ {path} must be a JSON array")
        for idx, q in enumerate(items, start=1):
            loc = f"{path}:{idx}"
            for field in ["id", "topic_id", "question", "difficulty", "novice_answer", "expert_answer"]:
                if field not in q:
                    raise SystemExit(f"❌ {loc} missing {field}")
            if q["id"] in seen:
                raise SystemExit(f"❌ Duplicate question id: {q['id']}")
            if q["topic_id"] not in topic_ids:
                raise SystemExit(f"❌ {q['id']} unknown topic_id: {q['topic_id']}")
            if q["difficulty"] not in VALID_DIFFICULTIES:
                raise SystemExit(f"❌ {q['id']} invalid difficulty: {q['difficulty']}")
            if not str(q["question"]).strip():
                raise SystemExit(f"❌ {q['id']} empty question")
            if not str(q["expert_answer"]).strip():
                raise SystemExit(f"❌ {q['id']} empty expert_answer")
            if "companies" in q and not isinstance(q["companies"], list):
                raise SystemExit(f"❌ {q['id']} companies must be a list")
            if "tags" in q and not isinstance(q["tags"], list):
                raise SystemExit(f"❌ {q['id']} tags must be a list")
            seen.add(q["id"])
            total += 1
    print(f"✅ Question data valid: {len(topics)} topics, {total} questions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
