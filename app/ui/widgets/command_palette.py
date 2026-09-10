"""Command palette: Ctrl+K quick-open for tools and app navigation."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QDialog, QLineEdit, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from app.core.app_context import AppContext
from app.ui import shortcuts as sc
from app.ui.icons import icon


@dataclass(frozen=True, slots=True)
class PaletteCommand:
    label: str
    subtitle: str
    action: Callable[[], None]


class CommandPalette(QDialog):
    """Modal overlay listing navigable commands, filtered as the user types."""

    def __init__(
        self,
        context: AppContext,
        static_commands: list[PaletteCommand],
        open_tool: Callable[[str], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("commandPalette")
        self.setWindowFlags(Qt.WindowType.Popup)
        self.setModal(True)
        self.setMinimumWidth(480)

        self._context = context
        self._static_commands = static_commands
        self._open_tool = open_tool
        self._commands: list[PaletteCommand] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Search tools and actions...")
        self._input.addAction(
            icon("search", "#646C7E", 15), QLineEdit.ActionPosition.LeadingPosition
        )
        self._input.textChanged.connect(self._on_query_changed)
        layout.addWidget(self._input)

        self._list = QListWidget()
        self._list.setObjectName("commandPaletteList")
        self._list.itemActivated.connect(self._on_item_activated)
        layout.addWidget(self._list)

        QShortcut(QKeySequence(sc.CLOSE_OVERLAY), self, self.close)
        self._input.installEventFilter(self)

        self._on_query_changed("")
        self._input.setFocus()

    def eventFilter(self, obj: object, event: object) -> bool:  # noqa: N802
        if obj is self._input and event.type() == event.Type.KeyPress:
            key = event.key()
            if key == Qt.Key.Key_Down:
                self._move_selection(1)
                return True
            if key == Qt.Key.Key_Up:
                self._move_selection(-1)
                return True
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self._activate_current()
                return True
        return super().eventFilter(obj, event)

    def _move_selection(self, delta: int) -> None:
        count = self._list.count()
        if count == 0:
            return
        row = self._list.currentRow()
        row = max(0, min(count - 1, (row if row >= 0 else 0) + delta))
        self._list.setCurrentRow(row)

    def _activate_current(self) -> None:
        item = self._list.currentItem()
        if item is not None:
            self._on_item_activated(item)

    def _on_query_changed(self, query: str) -> None:
        self._list.clear()
        self._commands = self._build_commands(query)
        for command in self._commands:
            item = QListWidgetItem(f"{command.label}  —  {command.subtitle}")
            self._list.addItem(item)
        if self._list.count() > 0:
            self._list.setCurrentRow(0)

    def _build_commands(self, query: str) -> list[PaletteCommand]:
        tool_commands = [
            PaletteCommand(meta.name, meta.category, lambda tid=meta.id: self._open_tool(tid))
            for meta in self._context.tool_registry.search(query)
        ]
        query_lower = query.strip().lower()
        action_commands = [
            cmd
            for cmd in self._static_commands
            if not query_lower or query_lower in cmd.label.lower()
        ]
        return tool_commands + action_commands

    def _on_item_activated(self, item: QListWidgetItem) -> None:
        row = self._list.row(item)
        if 0 <= row < len(self._commands):
            self._commands[row].action()
        self.close()
