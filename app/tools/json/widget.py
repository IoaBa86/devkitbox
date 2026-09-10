"""JSON Formatter tool page: format, minify, validate."""

from __future__ import annotations

from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from app.core.exceptions import FileOperationError, ValidationError
from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.json.logic import format_json, minify_json, validate_json
from app.ui.widgets.code_editor import CodeEditor
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="json_formatter",
    name="JSON Formatter",
    description="Format, validate and minify JSON locally.",
    category="Development",
    keywords=("json", "format", "formatter", "validate", "minify", "pretty"),
    shortcut="Ctrl+Enter",
)


class JsonFormatterTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("Indent"))
        self._indent_spin = QSpinBox()
        self._indent_spin.setRange(0, 8)
        self._indent_spin.setValue(2)
        toolbar.addWidget(self._indent_spin)

        self._sort_keys_check = QCheckBox("Sort keys")
        toolbar.addWidget(self._sort_keys_check)
        toolbar.addStretch(1)

        self._status_label = QLabel("")
        self._status_label.setObjectName("toolDescription")
        toolbar.addWidget(self._status_label)
        layout.addLayout(toolbar)

        panes = QHBoxLayout()
        panes.setSpacing(12)

        input_col = QVBoxLayout()
        input_col.addWidget(QLabel("INPUT"))
        self._input = CodeEditor(
            placeholder="Paste or drop a .json file here...", accept_drops=True
        )
        self._input.file_dropped.connect(self._on_file_dropped)
        input_col.addWidget(self._input)
        panes.addLayout(input_col)

        output_col = QVBoxLayout()
        output_col.addWidget(QLabel("OUTPUT"))
        self._output = CodeEditor(read_only=True)
        output_col.addWidget(self._output)
        panes.addLayout(output_col)

        layout.addLayout(panes, stretch=1)

        QShortcut(QKeySequence("Ctrl+Return"), self, self._format)
        QShortcut(QKeySequence("Ctrl+Enter"), self, self._format)

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

        load_button = QPushButton("Load File...")
        load_button.clicked.connect(self._load_file)
        layout.addWidget(load_button)

        copy_button = QPushButton("Copy")
        copy_button.clicked.connect(self._copy_output)
        layout.addWidget(copy_button)

        save_button = QPushButton("Save...")
        save_button.clicked.connect(self._save_output)
        layout.addWidget(save_button)

    def _format(self) -> None:
        self._run(
            lambda text: format_json(
                text, self._indent_spin.value(), self._sort_keys_check.isChecked()
            )
        )

    def _minify(self) -> None:
        self._run(minify_json)

    def _validate(self) -> None:
        text = self._input.toPlainText()
        try:
            validate_json(text)
        except ValidationError as exc:
            self._show_error(exc)
            return
        self._status_label.setText("Valid JSON")
        show_toast(self, "JSON is valid", "success")

    def _run(self, func) -> None:
        text = self._input.toPlainText()
        try:
            result = func(text)
        except ValidationError as exc:
            self._show_error(exc)
            return
        self._output.setPlainText(result)
        self._status_label.setText("")
        show_toast(self, "JSON formatted", "success")

    def _show_error(self, exc: ValidationError) -> None:
        location = ""
        if exc.line is not None:
            location = f" (line {exc.line}, column {exc.column})"
        message = f"{exc.message}{location}"
        self._status_label.setText(message)
        self._output.clear()
        show_toast(self, exc.message, "error")

    def _copy_output(self) -> None:
        text = self._output.toPlainText()
        if not text:
            show_toast(self, "Nothing to copy", "warning")
            return
        self.copy_to_clipboard(text)
        show_toast(self, "Copied to clipboard", "success")

    def _save_output(self) -> None:
        text = self._output.toPlainText()
        if not text:
            show_toast(self, "Nothing to save", "warning")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save JSON", "", "JSON Files (*.json)")
        if not path:
            return
        try:
            self.context.export_service.save_text(path, text)
        except FileOperationError as exc:
            show_toast(self, exc.message, "error")
            return
        show_toast(self, "File saved", "success")

    def _load_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Open JSON", "", "JSON Files (*.json)")
        if path:
            self._load_path(path)

    def _on_file_dropped(self, path: str) -> None:
        self._load_path(path)

    def _load_path(self, path: str) -> None:
        try:
            content = self.context.export_service.load_text(path)
        except FileOperationError as exc:
            show_toast(self, exc.message, "error")
            return
        self._input.setPlainText(content)
