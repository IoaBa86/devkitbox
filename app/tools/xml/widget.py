"""XML Formatter tool page: format, minify, validate."""

from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from app.core.exceptions import ValidationError
from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.xml.logic import format_xml, minify_xml, validate_xml
from app.ui.widgets.code_editor import CodeEditor
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="xml_formatter",
    name="XML Formatter",
    description="Format, validate and minify XML locally.",
    category="Development",
    keywords=("xml", "format", "formatter", "validate", "minify", "pretty"),
)


class XmlFormatterTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        self._status_label = QLabel("")
        self._status_label.setObjectName("toolDescription")
        layout.addWidget(self._status_label)

        panes = QHBoxLayout()
        panes.setSpacing(12)

        input_col = QVBoxLayout()
        input_col.addWidget(QLabel("INPUT"))
        self._input = CodeEditor(placeholder="<root>\n  <child>value</child>\n</root>")
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

        validate_button = QPushButton("Validate")
        validate_button.clicked.connect(self._validate)
        layout.addWidget(validate_button)

        layout.addStretch(1)

        copy_button = QPushButton("Copy")
        copy_button.clicked.connect(self._copy_output)
        layout.addWidget(copy_button)

    def _format(self) -> None:
        self._run(format_xml)

    def _minify(self) -> None:
        self._run(minify_xml)

    def _validate(self) -> None:
        try:
            validate_xml(self._input.toPlainText())
        except ValidationError as exc:
            self._show_error(exc)
            return
        self._status_label.setText("Valid XML")
        show_toast(self, "XML is valid", "success")

    def _run(self, func) -> None:
        text = self._input.toPlainText()
        try:
            result = func(text)
        except ValidationError as exc:
            self._show_error(exc)
            return
        self._output.setPlainText(result)
        self._status_label.setText("")
        show_toast(self, "XML formatted", "success")

    def _show_error(self, exc: ValidationError) -> None:
        location = ""
        if exc.line is not None:
            location = f" (line {exc.line}, column {exc.column})"
        self._status_label.setText(f"{exc.message}{location}")
        self._output.clear()
        show_toast(self, exc.message, "error")

    def _copy_output(self) -> None:
        text = self._output.toPlainText()
        if not text:
            show_toast(self, "Nothing to copy", "warning")
            return
        self.copy_to_clipboard(text)
        show_toast(self, "Copied to clipboard", "success")
