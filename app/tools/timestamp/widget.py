"""Timestamp Converter tool page: bidirectional Unix/UTC/local/ISO conversion."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from app.core.exceptions import ValidationError
from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.timestamp.logic import (
    TimestampResult,
    from_iso,
    from_unix_millis,
    from_unix_seconds,
    now,
)
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="timestamp_converter",
    name="Timestamp Converter",
    description="Convert Unix timestamps, UTC, local time, and ISO 8601.",
    category="Development",
    keywords=("timestamp", "unix", "epoch", "date", "time", "utc", "iso"),
)

_FORMATS = ["Unix seconds", "Unix milliseconds", "ISO 8601"]


class TimestampConverterTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        input_row = QHBoxLayout()
        self._format_combo = QComboBox()
        self._format_combo.addItems(_FORMATS)
        input_row.addWidget(self._format_combo)

        self._input_edit = QLineEdit()
        self._input_edit.setPlaceholderText("e.g. 1704110400 or 2024-01-01T12:00:00Z")
        self._input_edit.returnPressed.connect(self._convert)
        input_row.addWidget(self._input_edit, stretch=1)
        layout.addLayout(input_row)

        form = QFormLayout()
        self._unix_seconds_edit = self._readonly_field()
        self._unix_millis_edit = self._readonly_field()
        self._utc_edit = self._readonly_field()
        self._local_edit = self._readonly_field()
        self._iso_edit = self._readonly_field()
        form.addRow("Unix seconds", self._unix_seconds_edit)
        form.addRow("Unix milliseconds", self._unix_millis_edit)
        form.addRow("UTC", self._utc_edit)
        form.addRow("Local time", self._local_edit)
        form.addRow("ISO 8601", self._iso_edit)
        layout.addLayout(form)
        layout.addStretch(1)

        self._show_result(now())

    @staticmethod
    def _readonly_field() -> QLineEdit:
        edit = QLineEdit()
        edit.setReadOnly(True)
        return edit

    def build_actions(self, layout: QHBoxLayout) -> None:
        convert_button = QPushButton("Convert")
        convert_button.setObjectName("primaryButton")
        convert_button.clicked.connect(self._convert)
        layout.addWidget(convert_button)

        current_button = QPushButton("Current Timestamp")
        current_button.clicked.connect(self._use_current)
        layout.addWidget(current_button)
        layout.addStretch(1)

        copy_button = QPushButton("Copy All")
        copy_button.clicked.connect(self._copy_all)
        layout.addWidget(copy_button)

    def _convert(self) -> None:
        text = self._input_edit.text().strip()
        if not text:
            show_toast(self, "Enter a value to convert", "warning")
            return
        fmt = self._format_combo.currentText()
        try:
            if fmt == "Unix seconds":
                result = from_unix_seconds(float(text))
            elif fmt == "Unix milliseconds":
                result = from_unix_millis(float(text))
            else:
                result = from_iso(text)
        except (ValidationError, ValueError) as exc:
            message = exc.message if isinstance(exc, ValidationError) else "Invalid number"
            show_toast(self, message, "error")
            return
        self._show_result(result)
        show_toast(self, "Converted", "success")

    def _use_current(self) -> None:
        self._show_result(now())

    def _show_result(self, result: TimestampResult) -> None:
        self._unix_seconds_edit.setText(str(result.unix_seconds))
        self._unix_millis_edit.setText(str(result.unix_millis))
        self._utc_edit.setText(result.utc)
        self._local_edit.setText(result.local)
        self._iso_edit.setText(result.iso8601)

    def _copy_all(self) -> None:
        lines = [
            f"Unix seconds: {self._unix_seconds_edit.text()}",
            f"Unix milliseconds: {self._unix_millis_edit.text()}",
            f"UTC: {self._utc_edit.text()}",
            f"Local time: {self._local_edit.text()}",
            f"ISO 8601: {self._iso_edit.text()}",
        ]
        self.copy_to_clipboard("\n".join(lines))
        show_toast(self, "Copied to clipboard", "success")
