# -*- coding: utf-8 -*-
"""
NanoBat 可选持久化：SQLite 存储会话/历史，便于多轮恢复与技能扩展。
当前为占位，主流程不依赖；后续可在此接入会话与技能调用记录。
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "nanobat.db"


def get_conn():
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(_DB_PATH))


def init_schema(conn):
    """初始化表结构（按需调用）。"""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            channel TEXT,
            created_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
