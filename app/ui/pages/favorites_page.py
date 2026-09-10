"""Lists every tool the user has starred."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from app.core.app_context import AppContext
from app.ui.widgets.empty_state import EmptyState
from app.ui.widgets.responsive_grid import ResponsiveGrid
from app.ui.widgets.tool_card import ToolCard


class FavoritesPage(QWidget):
    open_tool = Signal(str)

    def __init__(self, context: AppContext, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.context = context

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        outer.addWidget(scroll)

        body = QWidget()
        self._layout = QVBoxLayout(body)
        self._layout.setContentsMargins(32, 28, 32, 28)
        self._layout.setSpacing(16)
        scroll.setWidget(body)

        title = QLabel("Favorites")
        title.setObjectName("pageTitle")
        self._layout.addWidget(title)

        self._empty_state = EmptyState(
            "star", "No favorite tools yet.", "Star a tool to pin it here."
        )
        self._layout.addWidget(self._empty_state)

        self._grid = ResponsiveGrid(min_item_width=200, max_columns=4)
        self._layout.addWidget(self._grid)
        self._layout.addStretch(1)

        self.refresh()

    def refresh(self) -> None:
        registry = self.context.tool_registry
        favorite_ids = self.context.history_service.get_favorite_ids()
        tools = [
            registry.get_by_id(tid).metadata for tid in favorite_ids if registry.get_by_id(tid)
        ]

        if not tools:
            self._grid.setVisible(False)
            self._grid.set_items([])
            self._empty_state.setVisible(True)
            return

        self._empty_state.setVisible(False)
        self._grid.setVisible(True)
        cards = []
        for metadata in tools:
            card = ToolCard(metadata)
            card.clicked.connect(self.open_tool)
            cards.append(card)
        self._grid.set_items(cards)
