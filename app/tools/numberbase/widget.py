"""Number Base Converter tool page: binary/octal/decimal/hex conversion."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from app.core.exceptions import ValidationError
from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.numberbase.logic import BASES, bit_representation, convert_all, parse_value
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="number_base_converter",
    name="Number Base Converter",
    description="Convert between binary, octal, decimal, and hexadecimal.",
    category="Development",
    keywords=("binary", "hex", "octal", "decimal", "base", "convert", "bitwise"),
)


class NumberBaseConverterTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("From"))
        self._from_combo = QComboBox()
        self._from_combo.addItems(list(BASES.keys()))
        self._from_combo.setCurrentText("Decimal")
        self._from_combo.currentTextChanged.connect(self._refresh)
        input_row.addWidget(self._from_combo)

        self._value_edit = QLineEdit()
        self._value_edit.setPlaceholderText("42")
        self._value_edit.textChanged.connect(self._refresh)
        input_row.addWidget(self._value_edit, stretch=1)
        layout.addLayout(input_row)

        form = QFormLayout()
        self._result_labels: dict[str, QLabel] = {}
        for name in BASES:
            label = QLabel("—")
            form.addRow(name, label)
            self._result_labels[name] = label
        layout.addLayout(form)

        layout.addWidget(QLabel("32-BIT REPRESENTATION"))
        self._bits_label = QLabel("—")
        self._bits_label.setObjectName("toolDescription")
        self._bits_label.setWordWrap(True)
        layout.addWidget(self._bits_label)

        layout.addStretch(1)

    def build_actions(self, layout: QHBoxLayout) -> None:
        copy_button = QPushButton("Copy Decimal")
        copy_button.setObjectName("primaryButton")
        copy_button.clicked.connect(self._copy_decimal)
        layout.addWidget(copy_button)
        layout.addStretch(1)

    def _refresh(self) -> None:
        from_base = BASES[self._from_combo.currentText()]
        text = self._value_edit.text()

        if not text.strip():
            for label in self._result_labels.values():
                label.setText("—")
            self._bits_label.setText("—")
            return

        try:
            results = convert_all(text, from_base)
            value = parse_value(text, from_base)
        except ValidationError:
            for label in self._result_labels.values():
                label.setText("Invalid")
            self._bits_label.setText("—")
            return

        for name, label in self._result_labels.items():
            label.setText(results[name])

        if -(2**31) <= value < 2**31:
            self._bits_label.setText(bit_representation(value))
        else:
            self._bits_label.setText("Out of 32-bit range")

    def _copy_decimal(self) -> None:
        text = self._result_labels["Decimal"].text()
        if not text or text in ("—", "Invalid"):
            show_toast(self, "Nothing to copy", "warning")
            return
        self.copy_to_clipboard(text)
        show_toast(self, "Copied to clipboard", "success")
