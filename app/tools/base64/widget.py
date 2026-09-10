"""Base64 tool page: text encode/decode plus file <-> Base64."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from app.core.exceptions import FileOperationError, ValidationError
from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.base64.logic import decode_text, decode_to_bytes, encode_bytes, encode_text
from app.ui.widgets.code_editor import CodeEditor
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="base64_tool",
    name="Base64",
    description="Encode and decode Base64 data, including URL-safe and files.",
    category="Encoding",
    keywords=("base64", "encode", "decode", "b64"),
)


class Base64Tool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        toolbar = QHBoxLayout()
        self._url_safe_check = QCheckBox("URL-safe")
        toolbar.addWidget(self._url_safe_check)
        toolbar.addStretch(1)
        layout.addLayout(toolbar)

        panes = QHBoxLayout()
        panes.setSpacing(12)

        input_col = QVBoxLayout()
        input_col.addWidget(QLabel("INPUT"))
        self._input = CodeEditor(placeholder="Text or Base64...")
        input_col.addWidget(self._input)
        panes.addLayout(input_col)

        output_col = QVBoxLayout()
        output_col.addWidget(QLabel("OUTPUT"))
        self._output = CodeEditor(read_only=True)
        output_col.addWidget(self._output)
        panes.addLayout(output_col)

        layout.addLayout(panes, stretch=1)

        file_row = QHBoxLayout()
        file_row.addWidget(QLabel("Files"))
        encode_file_button = QPushButton("Encode File...")
        encode_file_button.clicked.connect(self._encode_file)
        file_row.addWidget(encode_file_button)

        decode_file_button = QPushButton("Decode to File...")
        decode_file_button.clicked.connect(self._decode_to_file)
        file_row.addWidget(decode_file_button)
        file_row.addStretch(1)
        layout.addLayout(file_row)

    def build_actions(self, layout: QHBoxLayout) -> None:
        encode_button = QPushButton("Encode")
        encode_button.setObjectName("primaryButton")
        encode_button.clicked.connect(self._encode)
        layout.addWidget(encode_button)

        decode_button = QPushButton("Decode")
        decode_button.clicked.connect(self._decode)
        layout.addWidget(decode_button)

        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self._clear)
        layout.addWidget(clear_button)

        layout.addStretch(1)

        copy_button = QPushButton("Copy")
        copy_button.clicked.connect(self._copy_output)
        layout.addWidget(copy_button)

    def _encode(self) -> None:
        text = self._input.toPlainText()
        self._output.setPlainText(encode_text(text, self._url_safe_check.isChecked()))
        show_toast(self, "Encoded", "success")

    def _decode(self) -> None:
        text = self._input.toPlainText()
        try:
            self._output.setPlainText(decode_text(text, self._url_safe_check.isChecked()))
        except ValidationError as exc:
            show_toast(self, exc.message, "error")
            return
        show_toast(self, "Decoded", "success")

    def _clear(self) -> None:
        self._input.clear()
        self._output.clear()

    def _copy_output(self) -> None:
        text = self._output.toPlainText()
        if not text:
            show_toast(self, "Nothing to copy", "warning")
            return
        self.copy_to_clipboard(text)
        show_toast(self, "Copied to clipboard", "success")

    def _encode_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if not path:
            return
        try:
            data = self.context.export_service.load_bytes(path)
        except FileOperationError as exc:
            show_toast(self, exc.message, "error")
            return
        self._output.setPlainText(encode_bytes(data, self._url_safe_check.isChecked()))
        show_toast(self, "File encoded", "success")

    def _decode_to_file(self) -> None:
        text = self._input.toPlainText()
        try:
            data = decode_to_bytes(text, self._url_safe_check.isChecked())
        except ValidationError as exc:
            show_toast(self, exc.message, "error")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Decoded File")
        if not path:
            return
        try:
            self.context.export_service.save_bytes(path, data)
        except FileOperationError as exc:
            show_toast(self, exc.message, "error")
            return
        show_toast(self, "File saved", "success")
