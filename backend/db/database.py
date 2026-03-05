from __future__ import annotations

import json
import logging
from datetime import datetime

import aiosqlite

logger = logging.getLogger(__name__)

DB_PATH = "relay.db"

CREATE_WORKSPACES_TABLE = """
CREATE TABLE IF NOT EXISTS workspaces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    github_repos TEXT NOT NULL DEFAULT '[]',
    slack_channel_id TEXT NOT NULL DEFAULT '',
    schedule TEXT NOT NULL DEFAULT 'daily',
    created_at TEXT NOT NULL
)
"""

CREATE_BRIEFINGS_TABLE = """
CREATE TABLE IF NOT EXISTS briefings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id INTEGER,
    team_name TEXT NOT NULL DEFAULT 'Team',
    content TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL
)
"""


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CREATE_WORKSPACES_TABLE)
        await db.execute(CREATE_BRIEFINGS_TABLE)
        await db.commit()
    logger.info("Database initialized at %s", DB_PATH)


# ---- Workspaces ----

async def save_workspace(
    name: str,
    github_repos: list[str],
    slack_channel_id: str = "",
    schedule: str = "daily",
) -> int:
    now = datetime.utcnow().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO workspaces (name, github_repos, slack_channel_id, schedule, created_at)"
            " VALUES (?, ?, ?, ?, ?)",
            (name, json.dumps(github_repos), slack_channel_id, schedule, now),
        )
        await db.commit()
        return cursor.lastrowid  # type: ignore[return-value]


async def get_workspaces() -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM workspaces ORDER BY created_at DESC")
        rows = await cursor.fetchall()
        result = []
        for row in rows:
            d = dict(row)
            d["github_repos"] = json.loads(d.get("github_repos", "[]"))
            result.append(d)
        return result


# ---- Briefings ----

async def save_briefing(
    team_name: str,
    content: dict,
    workspace_id: int | None = None,
) -> int:
    now = datetime.utcnow().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO briefings (workspace_id, team_name, content, created_at) VALUES (?, ?, ?, ?)",
            (workspace_id, team_name, json.dumps(content), now),
        )
        await db.commit()
        return cursor.lastrowid  # type: ignore[return-value]


async def get_briefings(limit: int = 20) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM briefings ORDER BY created_at DESC LIMIT ?",
            (limit,),
        )
        rows = await cursor.fetchall()
        result = []
        for row in rows:
            d = dict(row)
            d["content"] = json.loads(d.get("content", "{}"))
            result.append(d)
        return result


async def get_briefing(briefing_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM briefings WHERE id = ?", (briefing_id,))
        row = await cursor.fetchone()
        if not row:
            return None
        d = dict(row)
        d["content"] = json.loads(d.get("content", "{}"))
        return d
