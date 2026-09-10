"""Case Converter tool page: live preview across common naming conventions."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.case.logic import CASE_CONVERTERS
from app.ui.widgets.code_editor import CodeEditor
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="case_converter",
    name="Case Converter",
    description="Convert text between common naming conventions instantly.",
    category="Text",
    keywords=("case", "camelcase", "snake_case", "kebab-case", "convert", "naming"),
)


class CaseConverterTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        layout.addWidget(QLabel("INPUT"))
        self._input = CodeEditor(placeholder="Type or paste text...")
        self._input.setMaximumHeight(100)
        self._input.textChanged.connect(self._refresh)
        layout.addWidget(self._input)

        self._table = QTableWidget(len(CASE_CONVERTERS), 2)
        self._table.setHorizontalHeaderLabels(["Case", "Result"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setColumnWidth(0, 140)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        for row, name in enumerate(CASE_CONVERTERS):
            self._table.setItem(row, 0, QTableWidgetItem(name))
            self._table.setItem(row, 1, QTableWidgetItem(""))
        layout.addWidget(self._table, stretch=1)

    def build_actions(self, layout: QHBoxLayout) -> None:
        copy_button = QPushButton("Copy Selected")
        copy_button.setObjectName("primaryButton")
        copy_button.clicked.connect(self._copy_selected)
        layout.addWidget(copy_button)
        layout.addStretch(1)

    def _refresh(self) -> None:
        text = self._input.toPlainText()
        for row, converter in enumerate(CASE_CONVERTERS.values()):
            self._table.setItem(row, 1, QTableWidgetItem(converter(text)))

    def _copy_selected(self) -> None:
        row = self._table.currentRow()
        if row < 0:
            show_toast(self, "Select a row to copy", "warning")
            return
        item = self._table.item(row, 1)
        text = item.text() if item else ""
        if not text:
            show_toast(self, "Nothing to copy", "warning")
            return
        self.copy_to_clipboard(text)
        show_toast(self, "Copied to clipboard", "success")
