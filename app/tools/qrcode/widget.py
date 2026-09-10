"""QR Code Generator tool page: encode text/URLs as a scannable QR code."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from app.core.exceptions import ValidationError
from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.qrcode.logic import ERROR_CORRECTION_LEVELS, generate_matrix
from app.ui.widgets.code_editor import CodeEditor
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="qr_code_generator",
    name="QR Code Generator",
    description="Encode text or a URL as a scannable QR code, entirely offline.",
    category="Generators",
    keywords=("qr", "qr code", "barcode", "generator", "encode"),
)

_MODULE_SIZE = 8


def _matrix_to_pixmap(matrix: list[list[bool]]) -> QPixmap:
    size = len(matrix)
    image = QImage(size * _MODULE_SIZE, size * _MODULE_SIZE, QImage.Format.Format_RGB32)
    image.fill(QColor("white"))

    painter = QPainter(image)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor("black"))
    for row_index, row in enumerate(matrix):
        for col_index, is_dark in enumerate(row):
            if is_dark:
                painter.drawRect(
                    col_index * _MODULE_SIZE, row_index * _MODULE_SIZE, _MODULE_SIZE, _MODULE_SIZE
                )
    painter.end()
    return QPixmap.fromImage(image)


class QrCodeGeneratorTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("Error correction"))
        self._error_correction_combo = QComboBox()
        self._error_correction_combo.addItems(list(ERROR_CORRECTION_LEVELS.keys()))
        self._error_correction_combo.setCurrentText("Medium (15%)")
        input_row.addWidget(self._error_correction_combo)
        input_row.addStretch(1)
        layout.addLayout(input_row)

        self._input = CodeEditor(placeholder="https://devkitbox.net")
        self._input.setMaximumHeight(80)
        layout.addWidget(self._input)

        self._preview_label = QLabel("No QR code yet")
        self._preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_label.setMinimumHeight(280)
        self._preview_label.setObjectName("colorSwatch")
        layout.addWidget(self._preview_label, stretch=1)

        self._pixmap: QPixmap | None = None

    def build_actions(self, layout: QHBoxLayout) -> None:
        generate_button = QPushButton("Generate")
        generate_button.setObjectName("primaryButton")
        generate_button.clicked.connect(self._generate)
        layout.addWidget(generate_button)
        layout.addStretch(1)

        save_button = QPushButton("Save PNG...")
        save_button.clicked.connect(self._save)
        layout.addWidget(save_button)

    def _generate(self) -> None:
        try:
            matrix = generate_matrix(
                self._input.toPlainText().strip(), self._error_correction_combo.currentText()
            )
        except ValidationError as exc:
            show_toast(self, exc.message, "error")
            return

        self._pixmap = _matrix_to_pixmap(matrix)
        self._preview_label.setPixmap(
            self._pixmap.scaled(
                280,
                280,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation,
            )
        )
        show_toast(self, "QR code generated", "success")

    def _save(self) -> None:
        if self._pixmap is None:
            show_toast(self, "Generate a QR code first", "warning")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save QR Code", "", "PNG Files (*.png)")
        if not path:
            return
        if not self._pixmap.save(path, "PNG"):
            show_toast(self, "Could not save file", "error")
            return
        show_toast(self, "Saved", "success")
