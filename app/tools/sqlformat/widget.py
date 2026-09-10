"""SQL Formatter tool page."""

from __future__ import annotations

from PySide6.QtWidgets import QCheckBox, QComboBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from app.core.exceptions import ValidationError
from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.sqlformat.logic import KEYWORD_CASES, format_sql, minify_sql
from app.ui.widgets.code_editor import CodeEditor
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="sql_formatter",
    name="SQL Formatter",
    description="Pretty-print or minify SQL statements locally.",
    category="Development",
    keywords=("sql", "format", "formatter", "pretty", "minify", "query"),
)


class SqlFormatterTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        options_row = QHBoxLayout()
        options_row.addWidget(QLabel("Keyword case"))
        self._case_combo = QComboBox()
        self._case_combo.addItems(list(KEYWORD_CASES))
        options_row.addWidget(self._case_combo)

        self._strip_comments_check = QCheckBox("Strip comments")
        options_row.addWidget(self._strip_comments_check)
        options_row.addStretch(1)
        layout.addLayout(options_row)

        panes = QHBoxLayout()
        panes.setSpacing(12)

        input_col = QVBoxLayout()
        input_col.addWidget(QLabel("INPUT"))
        self._input = CodeEditor(placeholder="select id, name from users where active = 1")
        input_col.addWidget(self._input)
        panes.addLayout(input_col)

        output_col = QVBoxLayout()
        output_col.addWidget(QLabel("OUTPUT"))
        self._output = CodeEditor(read_only=True)
        output_col.addWidget(self._output)
        panes.addLayout(output_col)

        layout.addLayout(panes, stretch=1)

    def build_actions(self, layout: QHBoxLayout) -> None:
        format_button = QPushButton("Format")
        format_button.setObjectName("primaryButton")
        format_button.clicked.connect(self._format)
        layout.addWidget(format_button)

        minify_button = QPushButton("Minify")
        minify_button.clicked.connect(self._minify)
        layout.addWidget(minify_button)
        layout.addStretch(1)

        copy_button = QPushButton("Copy")
        copy_button.clicked.connect(self._copy_output)
        layout.addWidget(copy_button)

    def _format(self) -> None:
        self._run(
            lambda text: format_sql(
                text, self._case_combo.currentText(), 2, self._strip_comments_check.isChecked()
            )
        )

    def _minify(self) -> None:
        self._run(minify_sql)

    def _run(self, func) -> None:
        text = self._input.toPlainText()
        try:
            result = func(text)
        except ValidationError as exc:
            show_toast(self, exc.message, "error")
            return
        self._output.setPlainText(result)
        show_toast(self, "Formatted", "success")

    def _copy_output(self) -> None:
        text = self._output.toPlainText()
        if not text:
            show_toast(self, "Nothing to copy", "warning")
            return
        self.copy_to_clipboard(text)
        show_toast(self, "Copied to clipboard", "success")
