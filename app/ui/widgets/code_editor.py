"""Monospace plain-text editor used by every tool that edits code/data."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QPlainTextEdit

from app.ui.theme import MONOSPACE_FONT_FAMILY


class CodeEditor(QPlainTextEdit):
    """A file can also be dropped onto any CodeEditor; ``file_dropped`` fires
    with the path and the caller decides whether/how to load it."""

    file_dropped = Signal(str)

    def __init__(
        self,
        placeholder: str = "",
        read_only: bool = False,
        accept_drops: bool = False,
        parent=None,
    ) -> None:
        super().__init__(parent)
        font = QFont()
        font.setFamilies([f.strip() for f in MONOSPACE_FONT_FAMILY.split(",")])
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setPointSize(10)
        self.setFont(font)
        self.setPlaceholderText(placeholder)
        self.setReadOnly(read_only)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(" ") * 4)
        self.setAcceptDrops(accept_drops)

    def dragEnterEvent(self, event) -> None:  # noqa: N802 (Qt override)
        if self.acceptDrops() and event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event) -> None:  # noqa: N802 (Qt override)
        urls = event.mimeData().urls()
        if self.acceptDrops() and urls:
            self.file_dropped.emit(urls[0].toLocalFile())
            event.acceptProposedAction()
        else:
            super().dropEvent(event)
