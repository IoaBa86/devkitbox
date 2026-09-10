"""Standard scaffolding every tool page is built on top of.

A concrete tool subclasses ``ToolWidget``, sets a class-level ``metadata``,
and implements :meth:`build_content` to fill the content area. The header
(title, description, favorite star) and the action bar are handled here so
every tool looks and behaves consistently, per the tool-page standard.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.models.tool import ToolMetadata
from app.ui.icons import icon
from app.ui.theme import current_palette

if TYPE_CHECKING:
    from app.core.app_context import AppContext


class ToolWidget(QWidget):
    """Base class for all tool pages. Not instantiated directly."""

    metadata: ToolMetadata
    favorite_toggled = Signal(str, bool)  # tool_id, is_favorite

    def __init__(self, context: AppContext, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.context = context
        self._is_favorite = context.history_service.is_favorite(self.metadata.id)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        root.addLayout(self._build_header())

        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(12)
        root.addLayout(self.content_layout, stretch=1)

        self.action_bar = QHBoxLayout()
        self.action_bar.setSpacing(8)
        root.addLayout(self.action_bar)

        self.build_content(self.content_layout)
        self.build_actions(self.action_bar)

    def _build_header(self) -> QVBoxLayout:
        header = QVBoxLayout()
        header.setSpacing(2)

        eyebrow = QLabel(self.metadata.category.upper())
        eyebrow.setObjectName("toolBreadcrumb")
        header.addWidget(eyebrow)

        title_row = QHBoxLayout()
        title = QLabel(self.metadata.name)
        title.setObjectName("pageTitle")
        title_row.addWidget(title)
        title_row.addStretch(1)

        self._favorite_button = QPushButton()
        self._favorite_button.setObjectName("favoriteButton")
        self._favorite_button.setFlat(True)
        self._favorite_button.setCheckable(True)
        self._favorite_button.setChecked(self._is_favorite)
        self._favorite_button.setIconSize(QSize(18, 18))
        self._favorite_button.setToolTip("Toggle favorite")
        self._favorite_button.clicked.connect(self._on_favorite_clicked)
        self._update_favorite_icon()
        title_row.addWidget(self._favorite_button)
        header.addLayout(title_row)

        description = QLabel(self.metadata.description)
        description.setObjectName("toolDescription")
        description.setWordWrap(True)
        description.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        header.addWidget(description)

        return header

    def _update_favorite_icon(self) -> None:
        app = QApplication.instance()
        palette = current_palette(app) if app else None
        warning = palette.warning if palette else "#FFB454"
        muted = palette.text_muted if palette else "#646C7E"
        icon_name = "star_filled" if self._is_favorite else "star"
        color = warning if self._is_favorite else muted
        self._favorite_button.setIcon(icon(icon_name, color, 18))

    def _on_favorite_clicked(self) -> None:
        is_fav = self.context.history_service.toggle_favorite(self.metadata.id)
        self._is_favorite = is_fav
        self._favorite_button.setChecked(is_fav)
        self._update_favorite_icon()
        self.favorite_toggled.emit(self.metadata.id, is_fav)

    @abstractmethod
    def build_content(self, layout: QVBoxLayout) -> None:
        """Populate the tool's main content area."""
        raise NotImplementedError

    def build_actions(self, layout: QHBoxLayout) -> None:
        """Populate the action bar. Optional — default is no actions."""

    def copy_to_clipboard(self, text: str) -> None:
        self.context.clipboard_service.copy(text)
