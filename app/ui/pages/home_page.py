"""Dashboard: quick tools, recently used, and category browsing."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from app.core.app_context import AppContext
from app.core.constants import APP_TAGLINE, TOOL_CATEGORIES
from app.ui.widgets.empty_state import EmptyState
from app.ui.widgets.responsive_grid import ResponsiveGrid
from app.ui.widgets.tool_card import CategoryCard, ToolCard


class HomePage(QWidget):
    open_tool = Signal(str)
    open_category = Signal(str)

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
        self._layout.setSpacing(28)
        scroll.setWidget(body)

        self._build_welcome()

        self._quick_tools_empty, self._quick_tools_grid = self._build_section("Quick Tools", 200)
        self._recent_empty, self._recent_grid = self._build_section("Recently Used", 200)
        self._categories_empty, self._categories_grid = self._build_section("Categories", 170)
        self._layout.addStretch(1)

        self.refresh()

    def _build_welcome(self) -> None:
        title = QLabel("Welcome to DevKitBox")
        title.setObjectName("pageTitle")
        self._layout.addWidget(title)

        subtitle = QLabel(APP_TAGLINE)
        subtitle.setObjectName("toolDescription")
        self._layout.addWidget(subtitle)

    def _build_section(self, title: str, min_item_width: int) -> tuple[QWidget, ResponsiveGrid]:
        header_row = QHBoxLayout()
        header_row.setSpacing(8)
        rule = QFrame()
        rule.setObjectName("sectionRule")
        rule.setFixedSize(4, 16)
        header_row.addWidget(rule)
        heading = QLabel(title)
        heading.setObjectName("sectionHeading")
        header_row.addWidget(heading)
        header_row.addStretch(1)
        self._layout.addLayout(header_row)

        empty_state = EmptyState("dot", "", "")
        empty_state.setVisible(False)
        self._layout.addWidget(empty_state)

        grid = ResponsiveGrid(min_item_width=min_item_width, max_columns=4)
        self._layout.addWidget(grid)

        return empty_state, grid

    def refresh(self) -> None:
        registry = self.context.tool_registry
        history = self.context.history_service

        favorite_ids = history.get_favorite_ids()
        favorite_tools = [
            registry.get_by_id(tid).metadata for tid in favorite_ids if registry.get_by_id(tid)
        ]
        self._fill_tools(
            self._quick_tools_empty,
            self._quick_tools_grid,
            favorite_tools,
            "star",
            "No favorite tools yet.",
            "Star a tool to pin it here.",
        )

        recent_ids = history.get_recent_ids(limit=6)
        recent_tools = [
            registry.get_by_id(tid).metadata for tid in recent_ids if registry.get_by_id(tid)
        ]
        self._fill_tools(
            self._recent_empty,
            self._recent_grid,
            recent_tools,
            "history",
            "No recent tools.",
            "Open a tool to start building your history.",
        )

        cards = []
        for category in TOOL_CATEGORIES:
            count = len(registry.get_by_category(category))
            card = CategoryCard(category, count)
            card.clicked.connect(self.open_category)
            cards.append(card)
        self._categories_empty.setVisible(False)
        self._categories_grid.setVisible(True)
        self._categories_grid.set_items(cards)

    def _fill_tools(
        self,
        empty_state: EmptyState,
        grid: ResponsiveGrid,
        tools,
        icon_name: str,
        title: str,
        subtitle: str,
    ) -> None:
        if tools:
            empty_state.setVisible(False)
            grid.setVisible(True)
            cards = []
            for metadata in tools:
                card = ToolCard(metadata)
                card.clicked.connect(self.open_tool)
                cards.append(card)
            grid.set_items(cards)
        else:
            grid.setVisible(False)
            grid.set_items([])
            empty_state.set_content(icon_name, title, subtitle)
            empty_state.setVisible(True)
