""".env Parser/Validator tool page: parse KEY=VALUE lines and flag issues."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.envparser.logic import parse_env, validate_env
from app.ui.widgets.code_editor import CodeEditor
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="env_parser",
    name=".env Parser/Validator",
    description="Parse KEY=VALUE lines and flag duplicates, empty values, and missing keys.",
    category="Development",
    keywords=("env", "dotenv", "environment", "variables", "parser", "validator"),
)


class EnvParserTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("Required keys (comma-separated, optional)"))
        self._required_keys_edit = QLineEdit()
        self._required_keys_edit.setPlaceholderText("DATABASE_URL, SECRET_KEY")
        input_row.addWidget(self._required_keys_edit, stretch=1)
        layout.addLayout(input_row)

        panes = QHBoxLayout()
        panes.setSpacing(12)

        input_col = QVBoxLayout()
        input_col.addWidget(QLabel("INPUT"))
        self._input = CodeEditor(placeholder="DATABASE_URL=postgres://localhost/db\nDEBUG=true")
        input_col.addWidget(self._input)
        panes.addLayout(input_col)

        output_col = QVBoxLayout()
        output_col.addWidget(QLabel("PARSED VARIABLES"))
        self._table = QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(["Key", "Value"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        output_col.addWidget(self._table)
        panes.addLayout(output_col)

        layout.addLayout(panes, stretch=1)

        layout.addWidget(QLabel("ISSUES"))
        self._issues_list = QListWidget()
        self._issues_list.setMaximumHeight(120)
        layout.addWidget(self._issues_list)

    def build_actions(self, layout: QHBoxLayout) -> None:
        parse_button = QPushButton("Parse")
        parse_button.setObjectName("primaryButton")
        parse_button.clicked.connect(self._parse)
        layout.addWidget(parse_button)
        layout.addStretch(1)

    def _parse(self) -> None:
        text = self._input.toPlainText()
        entries = parse_env(text)

        self._table.setRowCount(len(entries))
        for row, entry in enumerate(entries):
            self._table.setItem(row, 0, QTableWidgetItem(entry.key))
            self._table.setItem(row, 1, QTableWidgetItem(entry.value))

        required_keys = [
            key.strip() for key in self._required_keys_edit.text().split(",") if key.strip()
        ]
        issues = validate_env(text, required_keys)

        self._issues_list.clear()
        if not issues:
            self._issues_list.addItem("No issues found")
        else:
            for issue in issues:
                prefix = f"Line {issue.line_number}: " if issue.line_number else ""
                self._issues_list.addItem(f"{prefix}{issue.message}")

        show_toast(self, f"Parsed {len(entries)} variables", "success")
