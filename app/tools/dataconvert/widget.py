"""Data Converter tool page: JSON, YAML, and CSV, converted between each other."""

from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from app.core.exceptions import ValidationError
from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.dataconvert.logic import FORMATS, convert
from app.ui.widgets.code_editor import CodeEditor
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="data_converter",
    name="Data Converter",
    description="Convert between JSON, YAML, and CSV.",
    category="Development",
    keywords=("json", "yaml", "csv", "convert", "data", "format"),
)


class DataConverterTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        format_row = QHBoxLayout()
        format_row.addWidget(QLabel("From"))
        self._from_combo = QComboBox()
        self._from_combo.addItems(list(FORMATS))
        format_row.addWidget(self._from_combo)

        format_row.addWidget(QLabel("To"))
        self._to_combo = QComboBox()
        self._to_combo.addItems(list(FORMATS))
        self._to_combo.setCurrentText("YAML")
        format_row.addWidget(self._to_combo)

        swap_button = QPushButton("Swap")
        swap_button.clicked.connect(self._swap_formats)
        format_row.addWidget(swap_button)
        format_row.addStretch(1)
        layout.addLayout(format_row)

        panes = QHBoxLayout()
        panes.setSpacing(12)

        input_col = QVBoxLayout()
        input_col.addWidget(QLabel("INPUT"))
        self._input = CodeEditor(placeholder='{"key": "value"}')
        input_col.addWidget(self._input)
        panes.addLayout(input_col)

        output_col = QVBoxLayout()
        output_col.addWidget(QLabel("OUTPUT"))
        self._output = CodeEditor(read_only=True)
        output_col.addWidget(self._output)
        panes.addLayout(output_col)

        layout.addLayout(panes, stretch=1)

        self._status_label = QLabel("")
        layout.addWidget(self._status_label)

    def build_actions(self, layout: QHBoxLayout) -> None:
        convert_button = QPushButton("Convert")
        convert_button.setObjectName("primaryButton")
        convert_button.clicked.connect(self._convert)
        layout.addWidget(convert_button)
        layout.addStretch(1)

        copy_button = QPushButton("Copy")
        copy_button.clicked.connect(self._copy_output)
        layout.addWidget(copy_button)

    def _swap_formats(self) -> None:
        from_text = self._from_combo.currentText()
        self._from_combo.setCurrentText(self._to_combo.currentText())
        self._to_combo.setCurrentText(from_text)

    def _convert(self) -> None:
        try:
            result = convert(
                self._input.toPlainText(),
                self._from_combo.currentText(),
                self._to_combo.currentText(),
            )
        except ValidationError as exc:
            self._status_label.setText(exc.message)
            self._output.clear()
            return

        self._status_label.setText("")
        self._output.setPlainText(result)
        show_toast(self, "Converted", "success")

    def _copy_output(self) -> None:
        text = self._output.toPlainText()
        if not text:
            show_toast(self, "Nothing to copy", "warning")
            return
        self.copy_to_clipboard(text)
        show_toast(self, "Copied to clipboard", "success")
