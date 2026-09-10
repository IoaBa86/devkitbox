"""Clickable card representing a single tool, used on the dashboard and search results."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from app.models.tool import ToolMetadata
from app.ui.icons import category_icon_name, icon_pixmap
from app.ui.theme import elevate


def _make_badge(category: str, size: int = 38) -> QWidget:
    badge = QFrame()
    badge.setObjectName("iconBadge")
    badge.setFixedSize(size, size)
    layout = QHBoxLayout(badge)
    layout.setContentsMargins(0, 0, 0, 0)
    icon_label = QLabel()
    icon_label.setPixmap(icon_pixmap(category_icon_name(category), "#FFFFFF", 22))
    layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
    return badge


class ToolCard(QFrame):
    clicked = Signal(str)

    def __init__(self, metadata: ToolMetadata, parent=None) -> None:
        super().__init__(parent)
        self._tool_id = metadata.id
        self.setObjectName("cardWidget")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(112)
        self.setMinimumWidth(200)
        elevate(self, blur=18, y_offset=4, strength=55)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        layout.addWidget(_make_badge(metadata.category))

        name = QLabel(metadata.name)
        name.setStyleSheet("font-size: 14px; font-weight: 600;")
        layout.addWidget(name)

        description = QLabel(metadata.description)
        description.setObjectName("toolDescription")
        description.setWordWrap(True)
        layout.addWidget(description)
        layout.addStretch(1)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802 (Qt override)
        if event.button() == Qt.MouseButton.LeftButton and self.rect().contains(event.pos()):
            self.clicked.emit(self._tool_id)
        super().mouseReleaseEvent(event)


class CategoryCard(QFrame):
    clicked = Signal(str)

    def __init__(self, category: str, tool_count: int, parent=None) -> None:
        super().__init__(parent)
        self._category = category
        self.setObjectName("cardWidget")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(104)
        self.setMinimumWidth(160)
        elevate(self, blur=18, y_offset=4, strength=55)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        layout.addWidget(_make_badge(category))

        name = QLabel(category)
        name.setStyleSheet("font-size: 14px; font-weight: 600;")
        layout.addWidget(name)

        count_label = QLabel(f"{tool_count} tool{'s' if tool_count != 1 else ''}")
        count_label.setObjectName("toolDescription")
        layout.addWidget(count_label)
        layout.addStretch(1)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802 (Qt override)
        if event.button() == Qt.MouseButton.LeftButton and self.rect().contains(event.pos()):
            self.clicked.emit(self._category)
        super().mouseReleaseEvent(event)
