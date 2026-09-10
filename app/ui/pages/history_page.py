"""Recently used tools, with the option to clear local history."""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from app.core.app_context import AppContext
from app.ui.icons import category_icon_name, icon
from app.ui.theme import current_palette
from app.ui.widgets.empty_state import EmptyState


class HistoryPage(QWidget):
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

        header = QHBoxLayout()
        title = QLabel("History")
        title.setObjectName("pageTitle")
        header.addWidget(title)
        header.addStretch(1)
        clear_button = QPushButton("Clear Recent")
        clear_button.clicked.connect(self._clear_recent)
        header.addWidget(clear_button)
        self._layout.addLayout(header)

        note = QLabel(
            "Recently opened tools are tracked locally. Tool input/output content "
            "history is off by default — enable it in Settings > Privacy."
        )
        note.setObjectName("toolDescription")
        note.setWordWrap(True)
        self._layout.addWidget(note)

        self._content = QVBoxLayout()
        self._layout.addLayout(self._content)
        self._layout.addStretch(1)

        self.refresh()

    def _clear_recent(self) -> None:
        self.context.history_service.clear_recent()
        self.refresh()

    def refresh(self) -> None:
        while self._content.count():
            item = self._content.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        registry = self.context.tool_registry
        recent_ids = self.context.history_service.get_recent_ids(limit=50)
        tools = [registry.get_by_id(tid).metadata for tid in recent_ids if registry.get_by_id(tid)]

        if not tools:
            self._content.addWidget(
                EmptyState(
                    "history", "No recent tools.", "Open a tool to start building your history."
                )
            )
            return

        muted = self._muted_color()
        for metadata in tools:
            row = QPushButton(f"  {metadata.name}    ·    {metadata.category}")
            row.setObjectName("sidebarNavButton")
            row.setProperty("active", False)
            row.setIconSize(QSize(16, 16))
            row.setIcon(icon(category_icon_name(metadata.category), muted, 16))
            row.setCursor(Qt.CursorShape.PointingHandCursor)
            row.clicked.connect(lambda _=False, tid=metadata.id: self.open_tool.emit(tid))
            self._content.addWidget(row)

    @staticmethod
    def _muted_color() -> str:
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
        palette = current_palette(app) if app else None
        return palette.text_muted if palette else "#646C7E"
