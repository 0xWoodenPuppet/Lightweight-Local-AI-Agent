# storage.py
# ─────────────────────────────────────────────────────────
# SQLite local disk storage for conversation history & transcripts
# ─────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "chats.db"


def get_db_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db() -> None:
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                messages TEXT NOT NULL DEFAULT '[]',
                summary TEXT NOT NULL DEFAULT ''
            );
        """)
        conn.commit()


def list_conversations() -> List[Dict[str, Any]]:
    init_db()
    with get_db_connection() as conn:
        cursor = conn.execute("""
            SELECT id, title, created_at, updated_at, summary
            FROM conversations
            ORDER BY updated_at DESC
        """)
        return [dict(row) for row in cursor.fetchall()]


def get_conversation(conv_id: str) -> Optional[Dict[str, Any]]:
    init_db()
    with get_db_connection() as conn:
        cursor = conn.execute("""
            SELECT id, title, created_at, updated_at, messages, summary
            FROM conversations
            WHERE id = ?
        """, (conv_id,))
        row = cursor.fetchone()
        if not row:
            return None
        res = dict(row)
        try:
            res["messages"] = json.loads(res["messages"])
        except Exception:
            res["messages"] = []
        return res


def save_conversation(
    conv_id: str,
    title: str,
    messages: List[Dict[str, Any]],
    summary: Optional[str] = None
) -> Dict[str, Any]:
    init_db()
    now = datetime.now().isoformat()
    messages_json = json.dumps(messages, ensure_ascii=False)

    with get_db_connection() as conn:
        cursor = conn.execute("SELECT created_at, summary FROM conversations WHERE id = ?", (conv_id,))
        existing = cursor.fetchone()

        if existing:
            created_at = existing["created_at"]
            active_summary = summary if summary is not None else existing["summary"]
            conn.execute("""
                UPDATE conversations
                SET title = ?, updated_at = ?, messages = ?, summary = ?
                WHERE id = ?
            """, (title, now, messages_json, active_summary, conv_id))
        else:
            created_at = now
            active_summary = summary or ""
            conn.execute("""
                INSERT INTO conversations (id, title, created_at, updated_at, messages, summary)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (conv_id, title, created_at, now, messages_json, active_summary))
        conn.commit()

    return {
        "id": conv_id,
        "title": title,
        "created_at": created_at,
        "updated_at": now,
        "messages": messages,
        "summary": active_summary
    }


def delete_conversation(conv_id: str) -> bool:
    init_db()
    with get_db_connection() as conn:
        cursor = conn.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
        conn.commit()
        return cursor.rowcount > 0
