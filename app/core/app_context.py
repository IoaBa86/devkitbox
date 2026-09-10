"""Application-wide service container, constructed once at startup."""

from __future__ import annotations

import logging

from app.core.paths import get_db_path
from app.models.settings import AppSettings
from app.services.clipboard_service import ClipboardService
from app.services.database import DatabaseService
from app.services.export_service import ExportService
from app.services.history_service import HistoryService
from app.services.settings_service import SettingsService
from app.tools.registry import ToolRegistry


class AppContext:
    """Holds long-lived services and shared state, passed down to the UI."""

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger
        self.database = DatabaseService(get_db_path())
        self.database.connect()

        self.settings_service = SettingsService(self.database)
        self.settings: AppSettings = self.settings_service.load()

        self.history_service = HistoryService(self.database)
        self.clipboard_service = ClipboardService()
        self.export_service = ExportService()
        self.tool_registry = ToolRegistry()

    def shutdown(self) -> None:
        self.settings_service.save(self.settings)
        self.database.close()
        self.logger.info("DevKitBox shutting down cleanly")
