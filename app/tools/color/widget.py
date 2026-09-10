"""Color Picker/Converter tool page: HEX/RGB/HSL/HSV conversion and contrast check."""

from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.core.exceptions import ValidationError
from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.color.logic import (
    BLACK,
    WHITE,
    contrast_ratio,
    format_hsl,
    format_hsv,
    format_rgb,
    parse_hex,
    rgb_to_hex,
    rgb_to_hsl,
    rgb_to_hsv,
    wcag_level,
)
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="color_tool",
    name="Color Picker/Converter",
    description="Convert between HEX, RGB, HSL, and HSV, and check contrast ratios.",
    category="Design",
    keywords=("color", "colour", "hex", "rgb", "hsl", "hsv", "contrast", "wcag", "picker"),
)


class ColorTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("HEX"))
        self._hex_edit = QLineEdit("#7C5CFF")
        self._hex_edit.textChanged.connect(self._on_hex_changed)
        input_row.addWidget(self._hex_edit, stretch=1)

        pick_button = QPushButton("Pick...")
        pick_button.clicked.connect(self._open_picker)
        input_row.addWidget(pick_button)
        layout.addLayout(input_row)

        self._swatch = QWidget()
        self._swatch.setFixedHeight(64)
        self._swatch.setObjectName("colorSwatch")
        layout.addWidget(self._swatch)

        form = QFormLayout()
        self._rgb_label = QLabel("")
        self._hsl_label = QLabel("")
        self._hsv_label = QLabel("")
        form.addRow("RGB", self._rgb_label)
        form.addRow("HSL", self._hsl_label)
        form.addRow("HSV", self._hsv_label)
        layout.addLayout(form)

        layout.addWidget(QLabel("CONTRAST"))
        contrast_form = QFormLayout()
        self._contrast_white_label = QLabel("")
        self._contrast_black_label = QLabel("")
        contrast_form.addRow("On white", self._contrast_white_label)
        contrast_form.addRow("On black", self._contrast_black_label)
        layout.addLayout(contrast_form)

        layout.addStretch(1)
        self._refresh()

    def build_actions(self, layout: QHBoxLayout) -> None:
        copy_button = QPushButton("Copy HEX")
        copy_button.setObjectName("primaryButton")
        copy_button.clicked.connect(self._copy_hex)
        layout.addWidget(copy_button)
        layout.addStretch(1)

    def _open_picker(self) -> None:
        try:
            initial = parse_hex(self._hex_edit.text())
            initial_color = QColor(initial.r, initial.g, initial.b)
        except ValidationError:
            initial_color = QColor("#7C5CFF")

        color = QColorDialog.getColor(initial_color, self, "Pick a color")
        if color.isValid():
            self._hex_edit.setText(color.name())

    def _on_hex_changed(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        try:
            rgb = parse_hex(self._hex_edit.text())
        except ValidationError:
            self._swatch.setStyleSheet("background-color: transparent;")
            self._rgb_label.setText("—")
            self._hsl_label.setText("—")
            self._hsv_label.setText("—")
            self._contrast_white_label.setText("—")
            self._contrast_black_label.setText("—")
            return

        self._swatch.setStyleSheet(f"background-color: {rgb_to_hex(rgb)}; border-radius: 8px;")
        self._rgb_label.setText(format_rgb(rgb))
        self._hsl_label.setText(format_hsl(*rgb_to_hsl(rgb)))
        self._hsv_label.setText(format_hsv(*rgb_to_hsv(rgb)))

        white_ratio = contrast_ratio(rgb, WHITE)
        black_ratio = contrast_ratio(rgb, BLACK)
        self._contrast_white_label.setText(f"{white_ratio}:1 ({wcag_level(white_ratio)})")
        self._contrast_black_label.setText(f"{black_ratio}:1 ({wcag_level(black_ratio)})")

    def _copy_hex(self) -> None:
        try:
            rgb = parse_hex(self._hex_edit.text())
        except ValidationError as exc:
            show_toast(self, exc.message, "error")
            return
        self.copy_to_clipboard(rgb_to_hex(rgb))
        show_toast(self, "Copied to clipboard", "success")
