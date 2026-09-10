"""Reusable placeholder for pages/lists with nothing to show yet."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QFrame, QLabel, QVBoxLayout, QWidget

from app.ui.icons import icon_pixmap
from app.ui.theme import current_palette

_FALLBACK_MUTED = "#646C7E"


class EmptyState(QWidget):
    def __init__(
        self, icon_name: str, title: str, subtitle: str, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        # NOTE: do not call layout.setAlignment(AlignCenter) on the whole
        # QVBoxLayout — that forces every child to its sizeHint() and breaks
        # word-wrapped QLabel height, causing wrapped lines to overlap.
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(24, 32, 24, 32)

        badge = QFrame()
        badge.setObjectName("emptyBadge")
        badge.setFixedSize(52, 52)
        badge_layout = QVBoxLayout(badge)
        badge_layout.setContentsMargins(0, 0, 0, 0)
        self._icon_label = QLabel()
        badge_layout.addWidget(self._icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(badge, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(4)

        self._title_label = QLabel(title)
        self._title_label.setObjectName("emptyStateTitle")
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._title_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        self._subtitle_label = QLabel(subtitle)
        self._subtitle_label.setObjectName("emptyStateSubtitle")
        self._subtitle_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        self._subtitle_label.setWordWrap(True)
        self._subtitle_label.setMaximumWidth(320)
        # Fixed height (2 lines' worth) instead of relying on heightForWidth:
        # nested layouts negotiating heightForWidth for a wrapped QLabel is a
        # known Qt weak spot and was causing wrapped lines to mis-paint on top
        # of each other here.
        line_height = self._subtitle_label.fontMetrics().lineSpacing()
        self._subtitle_label.setFixedHeight(line_height * 2 + 4)
        layout.addWidget(self._subtitle_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        self._icon_name = icon_name
        self._refresh_icon()

    def set_content(self, icon_name: str, title: str, subtitle: str) -> None:
        self._icon_name = icon_name
        self._title_label.setText(title)
        self._subtitle_label.setText(subtitle)
        self._refresh_icon()

    def _refresh_icon(self) -> None:
        self._icon_label.setPixmap(icon_pixmap(self._icon_name, self._muted_color(), 24))

    @staticmethod
    def _muted_color() -> str:
        app = QApplication.instance()
        palette = current_palette(app) if app else None
        return palette.text_muted if palette else _FALLBACK_MUTED
