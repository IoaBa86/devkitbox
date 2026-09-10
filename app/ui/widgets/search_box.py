"""Global search input used in the title bar."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLineEdit

from app.ui.icons import icon


class SearchBox(QLineEdit):
    query_changed = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("searchBox")
        self.setPlaceholderText("Search tools...")
        self.setClearButtonEnabled(True)
        self._search_action = self.addAction(
            icon("search", "#646C7E", 15), QLineEdit.ActionPosition.LeadingPosition
        )
        self.textChanged.connect(self.query_changed)

    def set_icon_color(self, color: str) -> None:
        self._search_action.setIcon(icon("search", color, 15))
