"""Whitespace Cleaner tool page: normalize line endings, trim, collapse, tabs/spaces."""

from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.whitespace import logic
from app.ui.widgets.code_editor import CodeEditor
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="whitespace_cleaner",
    name="Whitespace Cleaner",
    description="Normalize line endings, trim, collapse, and convert tabs/spaces.",
    category="Text",
    keywords=("whitespace", "trim", "tabs", "spaces", "line endings", "clean"),
)


class WhitespaceCleanerTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        panes = QHBoxLayout()
        panes.setSpacing(12)

        input_col = QVBoxLayout()
        input_col.addWidget(QLabel("INPUT"))
        self._input = CodeEditor(placeholder="Paste text to clean...")
        input_col.addWidget(self._input)
        panes.addLayout(input_col)

        output_col = QVBoxLayout()
        output_col.addWidget(QLabel("OUTPUT"))
        self._output = CodeEditor(read_only=True)
        output_col.addWidget(self._output)
        panes.addLayout(output_col)

        layout.addLayout(panes, stretch=1)

    def build_actions(self, layout: QHBoxLayout) -> None:
        actions = (
            ("Trim Trailing", logic.trim_trailing_whitespace),
            ("Trim Lines", logic.trim_leading_trailing),
            ("Collapse Spaces", logic.collapse_spaces),
            ("Collapse Blank Lines", logic.collapse_blank_lines),
            ("Remove Blank Lines", logic.remove_blank_lines),
            ("Tabs to Spaces", logic.tabs_to_spaces),
            ("Spaces to Tabs", logic.spaces_to_tabs),
        )
        for label, func in actions:
            button = QPushButton(label)
            button.clicked.connect(lambda _=False, f=func: self._run(f))
            layout.addWidget(button)

        layout.addStretch(1)

        clean_all_button = QPushButton("Clean All")
        clean_all_button.setObjectName("primaryButton")
        clean_all_button.clicked.connect(lambda: self._run(logic.clean_all))
        layout.addWidget(clean_all_button)

        copy_button = QPushButton("Copy")
        copy_button.clicked.connect(self._copy_output)
        layout.addWidget(copy_button)

    def _run(self, func) -> None:
        self._output.setPlainText(func(self._input.toPlainText()))

    def _copy_output(self) -> None:
        text = self._output.toPlainText()
        if not text:
            show_toast(self, "Nothing to copy", "warning")
            return
        self.copy_to_clipboard(text)
        show_toast(self, "Copied to clipboard", "success")
