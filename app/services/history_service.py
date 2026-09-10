"""Favorites, recently-used tools, and opt-in content history."""

from __future__ import annotations

from datetime import UTC, datetime

from app.services.database import DatabaseService

MAX_RECENT = 10


class HistoryService:
    def __init__(self, db: DatabaseService) -> None:
        self._db = db

    # -- Favorites ---------------------------------------------------

    def is_favorite(self, tool_id: str) -> bool:
        row = self._db.query_one("SELECT 1 FROM favorites WHERE tool_id = ?", (tool_id,))
        return row is not None

    def toggle_favorite(self, tool_id: str) -> bool:
        if self.is_favorite(tool_id):
            self._db.execute("DELETE FROM favorites WHERE tool_id = ?", (tool_id,))
            return False
        self._db.execute(
            "INSERT INTO favorites (tool_id, created_at) VALUES (?, ?)",
            (tool_id, datetime.now(UTC).isoformat()),
        )
        return True

    def get_favorite_ids(self) -> list[str]:
        rows = self._db.query("SELECT tool_id FROM favorites ORDER BY created_at DESC")
        return [row["tool_id"] for row in rows]

    def clear_favorites(self) -> None:
        self._db.execute("DELETE FROM favorites")

    # -- Recently used -------------------------------------------------

    def record_recent(self, tool_id: str) -> None:
        now = datetime.now(UTC).isoformat()
        self._db.execute(
            "INSERT INTO recent_tools (tool_id, opened_at) VALUES (?, ?) "
            "ON CONFLICT(tool_id) DO UPDATE SET opened_at = excluded.opened_at",
            (tool_id, now),
        )

    def get_recent_ids(self, limit: int = MAX_RECENT) -> list[str]:
        rows = self._db.query(
            "SELECT tool_id FROM recent_tools ORDER BY opened_at DESC LIMIT ?", (limit,)
        )
        return [row["tool_id"] for row in rows]

    def clear_recent(self) -> None:
        self._db.execute("DELETE FROM recent_tools")

    # -- Opt-in content history ----------------------------------------

    def add_entry(self, tool_id: str, input_text: str, output_text: str) -> None:
        self._db.execute(
            "INSERT INTO history (tool_id, created_at, input, output) VALUES (?, ?, ?, ?)",
            (tool_id, datetime.now(UTC).isoformat(), input_text, output_text),
        )

    def get_entries(self, tool_id: str | None = None, limit: int = 100) -> list:
        if tool_id:
            return self._db.query(
                "SELECT * FROM history WHERE tool_id = ? ORDER BY created_at DESC LIMIT ?",
                (tool_id, limit),
            )
        return self._db.query("SELECT * FROM history ORDER BY created_at DESC LIMIT ?", (limit,))

    def clear_history(self) -> None:
        self._db.execute("DELETE FROM history")
