"""Clipboard access. Never persists content unless the caller opts in."""

from __future__ import annotations

from PySide6.QtWidgets import QApplication


class ClipboardService:
    def copy(self, text: str) -> None:
        clipboard = QApplication.clipboard()
        if clipboard is not None:
            clipboard.setText(text)

    def paste(self) -> str:
        clipboard = QApplication.clipboard()
        if clipboard is None:
            return ""
        return clipboard.text()
