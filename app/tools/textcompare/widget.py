"""Text Compare tool page: line-level diff with similarity score."""

from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.textcompare.logic import diff_stats, line_diff, similarity_ratio
from app.ui.widgets.code_editor import CodeEditor
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="text_compare",
    name="Text Compare",
    description="Compare two blocks of text and view a line-by-line diff.",
    category="Text",
    keywords=("diff", "compare", "text", "difference", "similarity"),
)


class TextCompareTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        panes = QHBoxLayout()
        panes.setSpacing(12)

        left_col = QVBoxLayout()
        left_col.addWidget(QLabel("LEFT"))
        self._left = CodeEditor(placeholder="Original text...")
        left_col.addWidget(self._left)
        panes.addLayout(left_col)

        right_col = QVBoxLayout()
        right_col.addWidget(QLabel("RIGHT"))
        self._right = CodeEditor(placeholder="Changed text...")
        right_col.addWidget(self._right)
        panes.addLayout(right_col)

        layout.addLayout(panes, stretch=1)

        self._stats_label = QLabel("")
        layout.addWidget(self._stats_label)

        layout.addWidget(QLabel("DIFF"))
        self._output = CodeEditor(read_only=True)
        layout.addWidget(self._output, stretch=1)

    def build_actions(self, layout: QHBoxLayout) -> None:
        compare_button = QPushButton("Compare")
        compare_button.setObjectName("primaryButton")
        compare_button.clicked.connect(self._compare)
        layout.addWidget(compare_button)
        layout.addStretch(1)

        copy_button = QPushButton("Copy Diff")
        copy_button.clicked.connect(self._copy_output)
        layout.addWidget(copy_button)

    def _compare(self) -> None:
        left = self._left.toPlainText()
        right = self._right.toPlainText()

        lines = line_diff(left, right)
        rendered = "\n".join(f"{line.marker} {line.text}" for line in lines)
        self._output.setPlainText(rendered)

        added, removed, unchanged = diff_stats(left, right)
        ratio = similarity_ratio(left, right)
        self._stats_label.setText(
            f"Similarity: {ratio * 100:.1f}%  |  +{added} added  -{removed} removed  {unchanged} unchanged"
        )
        show_toast(self, "Compared", "success")

    def _copy_output(self) -> None:
        text = self._output.toPlainText()
        if not text:
            show_toast(self, "Nothing to copy", "warning")
            return
        self.copy_to_clipboard(text)
        show_toast(self, "Copied to clipboard", "success")
