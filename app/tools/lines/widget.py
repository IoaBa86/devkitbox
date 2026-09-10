"""Line Tools tool page: sort, dedupe, trim, reverse, shuffle, number lines."""

from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.lines import logic
from app.ui.widgets.code_editor import CodeEditor
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="line_tools",
    name="Line Tools",
    description="Sort, deduplicate, trim, reverse, shuffle, or number lines.",
    category="Text",
    keywords=("lines", "sort", "duplicates", "trim", "reverse", "shuffle"),
)


class LineToolsTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        panes = QHBoxLayout()
        panes.setSpacing(12)

        input_col = QVBoxLayout()
        input_col.addWidget(QLabel("INPUT"))
        self._input = CodeEditor(placeholder="One item per line...")
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
            ("Sort A-Z", logic.sort_ascending),
            ("Sort Z-A", logic.sort_descending),
            ("Remove Duplicates", logic.remove_duplicates),
            ("Remove Empty", logic.remove_empty_lines),
            ("Trim", logic.trim_lines),
            ("Reverse", logic.reverse_lines),
            ("Shuffle", logic.shuffle_lines),
            ("Number Lines", logic.add_line_numbers),
        )
        for label, func in actions:
            button = QPushButton(label)
            button.clicked.connect(lambda _=False, f=func: self._run(f))
            layout.addWidget(button)

        layout.addStretch(1)
        copy_button = QPushButton("Copy")
        copy_button.setObjectName("primaryButton")
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
