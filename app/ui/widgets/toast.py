"""Non-blocking toast notifications, anchored to the bottom-right of a host widget."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QLabel, QWidget

_KIND_PREFIX = {"success": "✓", "warning": "⚠", "error": "✕"}


class Toast(QLabel):
    def __init__(self, message: str, kind: str, host: QWidget) -> None:
        super().__init__(host)
        self.setObjectName("toast")
        prefix = _KIND_PREFIX.get(kind, "")
        self.setText(f"{prefix} {message}".strip())
        self.setWindowFlags(Qt.WindowType.SubWindow)
        self.adjustSize()
        self._reposition(host)
        self.show()
        self.raise_()
        QTimer.singleShot(2200, self.deleteLater)

    def _reposition(self, host: QWidget) -> None:
        margin = 20
        x = host.width() - self.width() - margin
        y = host.height() - self.height() - margin
        self.move(max(margin, x), max(margin, y))


def show_toast(host: QWidget, message: str, kind: str = "success") -> None:
    Toast(message, kind, host)
