"""Image Base64 tool page: preview a pasted Base64/data-URI image, or
encode a local image file to Base64."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
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
from app.tools.base64.logic import encode_bytes
from app.tools.imagebase64.logic import (
    decode_image_base64,
    detect_image_format,
    encode_image_to_data_uri,
    format_byte_size,
)
from app.ui.widgets.code_editor import CodeEditor
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="image_base64",
    name="Image Base64",
    description="Preview a Base64/data-URI image, or encode a local image file to Base64.",
    category="Encoding",
    keywords=("image", "base64", "data uri", "preview", "png", "jpeg"),
)

_PREVIEW_SIZE = 240


class ImageBase64Tool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        panes = QHBoxLayout()
        panes.setSpacing(12)

        input_col = QVBoxLayout()
        input_col.addWidget(QLabel("BASE64 / DATA URI"))
        self._input = CodeEditor(placeholder="data:image/png;base64,iVBORw0KG...")
        input_col.addWidget(self._input)
        panes.addLayout(input_col)

        preview_col = QVBoxLayout()
        preview_col.addWidget(QLabel("PREVIEW"))
        self._preview_label = QLabel("No image")
        self._preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_label.setMinimumSize(_PREVIEW_SIZE, _PREVIEW_SIZE)
        self._preview_label.setObjectName("colorSwatch")
        preview_col.addWidget(self._preview_label)

        self._info_label = QLabel("")
        self._info_label.setObjectName("toolDescription")
        preview_col.addWidget(self._info_label)
        preview_col.addStretch(1)
        panes.addLayout(preview_col)

        layout.addLayout(panes, stretch=1)

        self._data_uri_check = QCheckBox("Include data: URI prefix when encoding")
        self._data_uri_check.setChecked(True)
        layout.addWidget(self._data_uri_check)

    def build_actions(self, layout: QHBoxLayout) -> None:
        preview_button = QPushButton("Preview")
        preview_button.setObjectName("primaryButton")
        preview_button.clicked.connect(self._preview)
        layout.addWidget(preview_button)

        load_button = QPushButton("Load Image...")
        load_button.clicked.connect(self._load_image)
        layout.addWidget(load_button)
        layout.addStretch(1)

        copy_button = QPushButton("Copy Base64")
        copy_button.clicked.connect(self._copy_input)
        layout.addWidget(copy_button)

    def _preview(self) -> None:
        text = self._input.toPlainText()
        try:
            data = decode_image_base64(text)
        except ValidationError as exc:
            show_toast(self, exc.message, "error")
            return

        pixmap = QPixmap()
        if not pixmap.loadFromData(data):
            show_toast(self, "Could not decode this as an image", "error")
            self._preview_label.setText("Invalid image")
            self._preview_label.setPixmap(QPixmap())
            self._info_label.setText("")
            return

        scaled = pixmap.scaled(
            _PREVIEW_SIZE,
            _PREVIEW_SIZE,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._preview_label.setPixmap(scaled)
        fmt = detect_image_format(data)
        self._info_label.setText(
            f"{fmt}  •  {pixmap.width()}x{pixmap.height()}px  •  {format_byte_size(len(data))}"
        )
        show_toast(self, "Image decoded", "success")

    def _load_image(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.gif *.bmp *.webp)"
        )
        if not path:
            return
        try:
            data = self.context.export_service.load_bytes(path)
        except FileOperationError as exc:
            show_toast(self, exc.message, "error")
            return

        if self._data_uri_check.isChecked():
            self._input.setPlainText(encode_image_to_data_uri(data))
        else:
            self._input.setPlainText(encode_bytes(data))
        self._preview()

    def _copy_input(self) -> None:
        text = self._input.toPlainText()
        if not text:
            show_toast(self, "Nothing to copy", "warning")
            return
        self.copy_to_clipboard(text)
        show_toast(self, "Copied to clipboard", "success")
