"""Typed read/write access to the ``settings`` table."""

from __future__ import annotations

import json
from dataclasses import fields

from app.models.settings import SETTINGS_FIELD_TYPES, AppSettings
from app.services.database import DatabaseService


class SettingsService:
    def __init__(self, db: DatabaseService) -> None:
        self._db = db

    def load(self) -> AppSettings:
        settings = AppSettings()
        rows = self._db.query("SELECT key, value FROM settings")
        stored = {row["key"]: row["value"] for row in rows}

        for f in fields(AppSettings):
            if f.name not in stored:
                continue
            raw = stored[f.name]
            field_type = SETTINGS_FIELD_TYPES[f.name]
            try:
                value = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                continue
            if isinstance(value, field_type) or field_type is bool:
                setattr(
                    settings, f.name, field_type(value) if field_type is not bool else bool(value)
                )
        return settings

    def set(self, key: str, value: object) -> None:
        if key not in SETTINGS_FIELD_TYPES:
            raise KeyError(f"Unknown setting: {key}")
        self._db.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, json.dumps(value)),
        )

    def save(self, settings: AppSettings) -> None:
        for f in fields(settings):
            self.set(f.name, getattr(settings, f.name))
