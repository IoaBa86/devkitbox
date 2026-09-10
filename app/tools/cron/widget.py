"""Cron Expression Explainer tool page: parse a 5-field cron expression,
show a plain-English description, and list upcoming run times."""

from __future__ import annotations

from datetime import datetime

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
)

from app.core.exceptions import ValidationError
from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.cron.logic import describe, next_run_times, parse_cron
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="cron_explainer",
    name="Cron Expression Explainer",
    description="Parse a cron expression, see what it means, and preview upcoming run times.",
    category="Development",
    keywords=("cron", "crontab", "schedule", "expression", "explain"),
)


class CronExplainerTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("Expression"))
        self._expression_edit = QLineEdit("*/15 9-17 * * 1-5")
        self._expression_edit.textChanged.connect(self._refresh)
        input_row.addWidget(self._expression_edit, stretch=1)
        layout.addLayout(input_row)

        self._description_label = QLabel("")
        self._description_label.setObjectName("toolDescription")
        self._description_label.setWordWrap(True)
        layout.addWidget(self._description_label)

        layout.addWidget(QLabel("NEXT 10 RUNS"))
        self._runs_list = QListWidget()
        layout.addWidget(self._runs_list, stretch=1)

        layout.addStretch(1)
        self._refresh()

    def build_actions(self, layout: QHBoxLayout) -> None:
        copy_button = QPushButton("Copy Description")
        copy_button.setObjectName("primaryButton")
        copy_button.clicked.connect(self._copy_description)
        layout.addWidget(copy_button)
        layout.addStretch(1)

    def _refresh(self) -> None:
        expression = self._expression_edit.text()
        try:
            schedule = parse_cron(expression)
        except ValidationError as exc:
            self._description_label.setText(exc.message)
            self._runs_list.clear()
            return

        self._description_label.setText(describe(schedule))

        runs = next_run_times(schedule, datetime.now(), count=10)
        self._runs_list.clear()
        if not runs:
            self._runs_list.addItem("No runs found in the next 4 years")
            return
        for run in runs:
            self._runs_list.addItem(run.strftime("%Y-%m-%d %H:%M (%A)"))

    def _copy_description(self) -> None:
        text = self._description_label.text()
        if not text:
            show_toast(self, "Nothing to copy", "warning")
            return
        self.copy_to_clipboard(text)
        show_toast(self, "Copied to clipboard", "success")
