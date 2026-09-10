from __future__ import annotations

import pytest

from app.core.exceptions import DatabaseError
from app.services.database import _MIGRATIONS, DatabaseService


def test_connect_creates_expected_tables(tmp_path):
    db = DatabaseService(tmp_path / "test.db")
    db.connect()

    tables = {row["name"] for row in db.query("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"settings", "favorites", "recent_tools", "history", "api_requests"} <= tables

    version = db.conn.execute("PRAGMA user_version").fetchone()[0]
    assert version == len(_MIGRATIONS)
    db.close()


def test_migration_does_not_run_twice(tmp_path):
    path = tmp_path / "test.db"
    db = DatabaseService(path)
    db.connect()
    db.execute("INSERT INTO settings (key, value) VALUES ('theme', '\"dark\"')")
    db.close()

    db2 = DatabaseService(path)
    db2.connect()
    row = db2.query_one("SELECT value FROM settings WHERE key = 'theme'")
    assert row["value"] == '"dark"'
    db2.close()


def test_query_before_connect_raises(tmp_path):
    db = DatabaseService(tmp_path / "unused.db")
    with pytest.raises(DatabaseError):
        db.query("SELECT 1")


def test_execute_wraps_sqlite_errors(tmp_path):
    db = DatabaseService(tmp_path / "test.db")
    db.connect()
    with pytest.raises(DatabaseError):
        db.execute("INSERT INTO not_a_table (x) VALUES (1)")
    db.close()
