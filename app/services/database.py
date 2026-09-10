"""SQLite access layer with versioned migrations.

Schema version is tracked via SQLite's built-in ``PRAGMA user_version``.
Migrations are a plain ordered list of SQL scripts; each is applied exactly
once, in order, inside a transaction. Existing data is never dropped by a
migration — only additive schema changes belong here.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Sequence
from pathlib import Path

from app.core.exceptions import DatabaseError
from app.core.logging import get_logger

logger = get_logger("database")

_MIGRATIONS: list[str] = [
    # v1 — initial schema
    """
    CREATE TABLE IF NOT EXISTS settings (
        key   TEXT PRIMARY KEY,
        value TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS favorites (
        tool_id    TEXT PRIMARY KEY,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS recent_tools (
        tool_id   TEXT PRIMARY KEY,
        opened_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS history (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        tool_id    TEXT NOT NULL,
        created_at TEXT NOT NULL,
        input      TEXT,
        output     TEXT
    );

    CREATE TABLE IF NOT EXISTS api_requests (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        name       TEXT,
        method     TEXT NOT NULL,
        url        TEXT NOT NULL,
        params     TEXT,
        headers    TEXT,
        body       TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """,
]


class DatabaseService:
    """Owns the single SQLite connection and applies pending migrations."""

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._conn: sqlite3.Connection | None = None

    def connect(self) -> None:
        try:
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(self._db_path))
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            self._conn = conn
            self._migrate()
        except sqlite3.Error as exc:
            raise DatabaseError(
                "Could not open the local database.",
                detail=str(exc),
            ) from exc

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            raise DatabaseError("Database is not connected.")
        return self._conn

    def _migrate(self) -> None:
        conn = self.conn
        current_version = conn.execute("PRAGMA user_version").fetchone()[0]
        target_version = len(_MIGRATIONS)

        if current_version >= target_version:
            return

        logger.info("Migrating database from v%d to v%d", current_version, target_version)
        try:
            for version in range(current_version, target_version):
                conn.executescript(_MIGRATIONS[version])
                conn.execute(f"PRAGMA user_version = {version + 1}")
            conn.commit()
        except sqlite3.Error as exc:
            conn.rollback()
            raise DatabaseError(
                "Database migration failed. Your existing data was not modified.",
                detail=str(exc),
            ) from exc

    def execute(self, sql: str, params: Sequence = ()) -> sqlite3.Cursor:
        try:
            cur = self.conn.execute(sql, params)
            self.conn.commit()
            return cur
        except sqlite3.Error as exc:
            raise DatabaseError("A database operation failed.", detail=str(exc)) from exc

    def query(self, sql: str, params: Sequence = ()) -> list[sqlite3.Row]:
        try:
            return self.conn.execute(sql, params).fetchall()
        except sqlite3.Error as exc:
            raise DatabaseError("A database query failed.", detail=str(exc)) from exc

    def query_one(self, sql: str, params: Sequence = ()) -> sqlite3.Row | None:
        try:
            return self.conn.execute(sql, params).fetchone()
        except sqlite3.Error as exc:
            raise DatabaseError("A database query failed.", detail=str(exc)) from exc
