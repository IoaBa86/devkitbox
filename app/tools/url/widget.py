"""URL tool page: encode/decode, query-string parsing, and query-string building."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.url.logic import (
    build_query_string,
    decode_url,
    encode_component,
    encode_url,
    parse_lines_to_pairs,
    parse_query_string,
)
from app.ui.widgets.code_editor import CodeEditor
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="url_tool",
    name="URL Encoder/Decoder",
    description="Encode, decode, and parse URLs and query strings.",
    category="Encoding",
    keywords=("url", "encode", "decode", "query", "params", "uri"),
)


class UrlTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        self._component_check = QCheckBox("Encode as component (escape all reserved characters)")
        layout.addWidget(self._component_check)

        panes = QHBoxLayout()
        panes.setSpacing(12)
        input_col = QVBoxLayout()
        input_col.addWidget(QLabel("INPUT"))
        self._input = CodeEditor()
        input_col.addWidget(self._input)
        panes.addLayout(input_col)

        output_col = QVBoxLayout()
        output_col.addWidget(QLabel("OUTPUT"))
        self._output = CodeEditor(read_only=True)
        output_col.addWidget(self._output)
        panes.addLayout(output_col)
        layout.addLayout(panes)

        encode_row = QHBoxLayout()
        encode_button = QPushButton("Encode")
        encode_button.setObjectName("primaryButton")
        encode_button.clicked.connect(self._encode)
        encode_row.addWidget(encode_button)
        decode_button = QPushButton("Decode")
        decode_button.clicked.connect(self._decode)
        encode_row.addWidget(decode_button)
        encode_row.addStretch(1)
        copy_button = QPushButton("Copy")
        copy_button.clicked.connect(self._copy_output)
        encode_row.addWidget(copy_button)
        layout.addLayout(encode_row)

        layout.addWidget(QLabel("Parse query string"))
        parse_row = QHBoxLayout()
        self._query_edit = QLineEdit()
        self._query_edit.setPlaceholderText("https://example.com/search?page=2&sort=newest")
        parse_row.addWidget(self._query_edit, stretch=1)
        parse_button = QPushButton("Parse")
        parse_button.clicked.connect(self._parse_query)
        parse_row.addWidget(parse_button)
        layout.addLayout(parse_row)

        self._params_table = QTableWidget(0, 2)
        self._params_table.setHorizontalHeaderLabels(["Parameter", "Value"])
        self._params_table.horizontalHeader().setStretchLastSection(True)
        self._params_table.verticalHeader().setVisible(False)
        self._params_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._params_table.setMaximumHeight(140)
        layout.addWidget(self._params_table)

        layout.addWidget(QLabel("Build query string (one key=value per line)"))
        builder_row = QHBoxLayout()
        self._builder_edit = CodeEditor(placeholder="page=2\nsort=newest")
        self._builder_edit.setMaximumHeight(80)
        builder_row.addWidget(self._builder_edit, stretch=1)
        layout.addLayout(builder_row)

        build_row = QHBoxLayout()
        build_button = QPushButton("Build")
        build_button.clicked.connect(self._build_query)
        build_row.addWidget(build_button)
        self._built_query_edit = QLineEdit()
        self._built_query_edit.setReadOnly(True)
        build_row.addWidget(self._built_query_edit, stretch=1)
        layout.addLayout(build_row)

    def build_actions(self, layout: QHBoxLayout) -> None:
        pass

    def _encode(self) -> None:
        text = self._input.toPlainText()
        func = encode_component if self._component_check.isChecked() else encode_url
        self._output.setPlainText(func(text))
        show_toast(self, "Encoded", "success")

    def _decode(self) -> None:
        text = self._input.toPlainText()
        self._output.setPlainText(decode_url(text))
        show_toast(self, "Decoded", "success")

    def _copy_output(self) -> None:
        text = self._output.toPlainText()
        if not text:
            show_toast(self, "Nothing to copy", "warning")
            return
        self.copy_to_clipboard(text)
        show_toast(self, "Copied to clipboard", "success")

    def _parse_query(self) -> None:
        pairs = parse_query_string(self._query_edit.text())
        self._params_table.setRowCount(len(pairs))
        for row, (key, value) in enumerate(pairs):
            self._params_table.setItem(row, 0, QTableWidgetItem(key))
            self._params_table.setItem(row, 1, QTableWidgetItem(value))
        if not pairs:
            show_toast(self, "No query parameters found", "warning")

    def _build_query(self) -> None:
        pairs = parse_lines_to_pairs(self._builder_edit.toPlainText())
        if not pairs:
            show_toast(self, "Enter at least one key=value line", "warning")
            return
        self._built_query_edit.setText(build_query_string(pairs))
