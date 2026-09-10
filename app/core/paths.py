"""Filesystem locations for user data, config, and logs.

Uses Qt's standard-paths resolution so behavior is correct across Windows
versions without hand-rolling %LOCALAPPDATA% logic.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QStandardPaths

from app.core.constants import DB_FILENAME, LOG_FILENAME


def get_resource_root() -> Path:
    """Base directory for bundled read-only resources (e.g. ``assets/``).

    A PyInstaller build doesn't run from source, so a source-relative
    ``Path(__file__).parent...`` walk breaks once frozen — ``sys._MEIPASS``
    (onefile) or the executable's own directory (onedir) is where bundled
    data actually lands instead.
    """
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parent.parent.parent


def get_app_data_dir() -> Path:
    """Per-user application data directory, e.g. %LOCALAPPDATA%/DevKitBox."""
    base = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    path = Path(base)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_log_dir() -> Path:
    path = get_app_data_dir() / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_log_file() -> Path:
    return get_log_dir() / LOG_FILENAME


def get_db_path() -> Path:
    return get_app_data_dir() / DB_FILENAME


def ensure_dirs() -> None:
    get_app_data_dir()
    get_log_dir()
