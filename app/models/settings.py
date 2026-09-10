"""Typed application settings, persisted via SettingsService as key/value rows."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AppSettings:
    # Appearance
    theme: str = "dark"  # "light" | "dark" | "system"
    accent_color: str = "#7C5CFF"

    # Editor
    editor_font_size: int = 13
    editor_tab_size: int = 2
    editor_word_wrap: bool = True

    # Behavior
    launch_on_startup: bool = False
    minimize_to_tray: bool = False
    restore_previous_tool: bool = True
    last_tool_id: str = ""

    # Privacy
    tool_history_enabled: bool = False
    clipboard_history_enabled: bool = False

    # Window
    sidebar_collapsed: bool = False

    # Onboarding
    has_completed_onboarding: bool = False

    # Network (API Client)
    request_timeout_seconds: int = 30
    http_proxy_url: str = ""
    verify_ssl_certificates: bool = True

    # Updates
    check_for_updates_enabled: bool = False


SETTINGS_FIELD_TYPES: dict[str, type] = {
    "theme": str,
    "accent_color": str,
    "editor_font_size": int,
    "editor_tab_size": int,
    "editor_word_wrap": bool,
    "launch_on_startup": bool,
    "minimize_to_tray": bool,
    "restore_previous_tool": bool,
    "last_tool_id": str,
    "tool_history_enabled": bool,
    "clipboard_history_enabled": bool,
    "sidebar_collapsed": bool,
    "has_completed_onboarding": bool,
    "request_timeout_seconds": int,
    "http_proxy_url": str,
    "verify_ssl_certificates": bool,
    "check_for_updates_enabled": bool,
}
