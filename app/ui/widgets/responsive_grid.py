"""A grid that re-flows its items into more/fewer columns as it's resized.

Used for every card grid (dashboard, favorites, categories, search) so the
shell adapts from a single narrow column up to a wide multi-column layout
instead of a fixed column count that either wastes space or overflows.
"""

from __future__ import annotations

from PySide6.QtWidgets import QGridLayout, QWidget


class ResponsiveGrid(QWidget):
    def __init__(
        self,
        min_item_width: int = 200,
        spacing: int = 12,
        max_columns: int = 4,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._min_item_width = min_item_width
        self._max_columns = max_columns
        self._items: list[QWidget] = []
        self._current_columns = 0

        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(spacing)

    def set_items(self, items: list[QWidget]) -> None:
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self._items = list(items)
        self._current_columns = 0
        self._relayout()

    def resizeEvent(self, event) -> None:  # noqa: N802 (Qt override)
        super().resizeEvent(event)
        self._relayout()

    def _relayout(self) -> None:
        if not self._items:
            return
        width = self.width() or self._min_item_width
        columns = max(1, min(self._max_columns, width // self._min_item_width))
        if columns == self._current_columns:
            return
        self._current_columns = columns
        while self._layout.count():
            self._layout.takeAt(0)
        for index, widget in enumerate(self._items):
            self._layout.addWidget(widget, index // columns, index % columns)
