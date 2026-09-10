"""HTML Entity Encoder/Decoder tool page."""

from __future__ import annotations

from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.htmlentities.logic import decode_entities, encode_entities
from app.ui.widgets.code_editor import CodeEditor
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="html_entities",
    name="HTML Entity Encoder/Decoder",
    description="Escape or unescape HTML entities like &amp;, &lt;, and &quot;.",
    category="Encoding",
    keywords=("html", "entity", "entities", "escape", "unescape", "encode", "decode"),
)


class HtmlEntitiesTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        self._quotes_check = QCheckBox("Escape quotes too")
        self._quotes_check.setChecked(True)
        layout.addWidget(self._quotes_check)

        panes = QHBoxLayout()
        panes.setSpacing(12)

        input_col = QVBoxLayout()
        input_col.addWidget(QLabel("INPUT"))
        self._input = CodeEditor(placeholder='<div class="a">Tom & Jerry</div>')
        input_col.addWidget(self._input)
        panes.addLayout(input_col)

        output_col = QVBoxLayout()
        output_col.addWidget(QLabel("OUTPUT"))
        self._output = CodeEditor(read_only=True)
        output_col.addWidget(self._output)
        panes.addLayout(output_col)

        layout.addLayout(panes, stretch=1)

    def build_actions(self, layout: QHBoxLayout) -> None:
        encode_button = QPushButton("Encode")
        encode_button.setObjectName("primaryButton")
        encode_button.clicked.connect(self._encode)
        layout.addWidget(encode_button)

        decode_button = QPushButton("Decode")
        decode_button.clicked.connect(self._decode)
        layout.addWidget(decode_button)
        layout.addStretch(1)

        copy_button = QPushButton("Copy")
        copy_button.clicked.connect(self._copy_output)
        layout.addWidget(copy_button)

    def _encode(self) -> None:
        text = self._input.toPlainText()
        self._output.setPlainText(encode_entities(text, self._quotes_check.isChecked()))
        show_toast(self, "Encoded", "success")

    def _decode(self) -> None:
        text = self._input.toPlainText()
        self._output.setPlainText(decode_entities(text))
        show_toast(self, "Decoded", "success")

    def _copy_output(self) -> None:
        text = self._output.toPlainText()
        if not text:
            show_toast(self, "Nothing to copy", "warning")
            return
        self.copy_to_clipboard(text)
        show_toast(self, "Copied to clipboard", "success")
