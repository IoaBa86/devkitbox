"""Text Statistics tool page: live character/word/line counts as you type."""

from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QHBoxLayout, QLabel, QVBoxLayout

from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.text_stats.logic import compute_stats
from app.ui.widgets.code_editor import CodeEditor

METADATA = ToolMetadata(
    id="text_statistics",
    name="Text Statistics",
    description="Count characters, words, lines, and estimate reading time.",
    category="Text",
    keywords=("text", "statistics", "count", "words", "characters", "reading time"),
)


class TextStatisticsTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        layout.addWidget(QLabel("INPUT"))
        self._input = CodeEditor(placeholder="Type or paste text...")
        self._input.textChanged.connect(self._refresh)
        layout.addWidget(self._input, stretch=1)

        form = QFormLayout()
        self._characters_label = QLabel("0")
        self._characters_no_spaces_label = QLabel("0")
        self._words_label = QLabel("0")
        self._lines_label = QLabel("0")
        self._paragraphs_label = QLabel("0")
        self._bytes_label = QLabel("0")
        self._reading_time_label = QLabel("0 min")
        form.addRow("Characters", self._characters_label)
        form.addRow("Characters (no spaces)", self._characters_no_spaces_label)
        form.addRow("Words", self._words_label)
        form.addRow("Lines", self._lines_label)
        form.addRow("Paragraphs", self._paragraphs_label)
        form.addRow("Bytes (UTF-8)", self._bytes_label)
        form.addRow("Estimated reading time", self._reading_time_label)
        layout.addLayout(form)

    def build_actions(self, layout: QHBoxLayout) -> None:
        pass

    def _refresh(self) -> None:
        stats = compute_stats(self._input.toPlainText())
        self._characters_label.setText(str(stats.characters))
        self._characters_no_spaces_label.setText(str(stats.characters_no_spaces))
        self._words_label.setText(str(stats.words))
        self._lines_label.setText(str(stats.lines))
        self._paragraphs_label.setText(str(stats.paragraphs))
        self._bytes_label.setText(str(stats.byte_count))
        minutes = stats.reading_time_minutes
        if minutes < 1:
            self._reading_time_label.setText("< 1 min")
        else:
            self._reading_time_label.setText(f"{minutes:.1f} min")
