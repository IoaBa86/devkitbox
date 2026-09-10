"""JWT Encoder tool page: build an HMAC-signed test token.

Pairs with the JWT Decoder — HS256/384/512 only, for building local test
tokens. No key-pair management, so RS/ES algorithms aren't offered.
"""

from __future__ import annotations

import json

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from app.core.exceptions import ValidationError
from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.jwt.logic import HMAC_ALGORITHMS, encode_jwt
from app.ui.widgets.code_editor import CodeEditor
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="jwt_encoder",
    name="JWT Encoder",
    description="Build an HMAC-signed JWT from claims and a secret, for local testing.",
    category="Development",
    keywords=("jwt", "json web token", "encode", "sign", "hmac", "auth"),
)

_DEFAULT_PAYLOAD = '{\n  "sub": "1234567890",\n  "name": "Test User",\n  "iat": 1700000000\n}'


class JwtEncoderTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        options_row = QHBoxLayout()
        options_row.addWidget(QLabel("Algorithm"))
        self._algorithm_combo = QComboBox()
        self._algorithm_combo.addItems(list(HMAC_ALGORITHMS.keys()))
        options_row.addWidget(self._algorithm_combo)

        options_row.addWidget(QLabel("Secret"))
        self._secret_edit = QLineEdit("your-256-bit-secret")
        options_row.addWidget(self._secret_edit, stretch=1)
        layout.addLayout(options_row)

        layout.addWidget(QLabel("PAYLOAD (JSON claims)"))
        self._payload_input = CodeEditor(placeholder='{"sub": "1234567890"}')
        self._payload_input.setPlainText(_DEFAULT_PAYLOAD)
        layout.addWidget(self._payload_input)

        layout.addWidget(QLabel("TOKEN"))
        self._output = CodeEditor(read_only=True)
        self._output.setMaximumHeight(100)
        layout.addWidget(self._output)

        self._status_label = QLabel("")
        self._status_label.setObjectName("toolDescription")
        layout.addWidget(self._status_label)

    def build_actions(self, layout: QHBoxLayout) -> None:
        generate_button = QPushButton("Generate")
        generate_button.setObjectName("primaryButton")
        generate_button.clicked.connect(self._generate)
        layout.addWidget(generate_button)
        layout.addStretch(1)

        copy_button = QPushButton("Copy Token")
        copy_button.clicked.connect(self._copy_output)
        layout.addWidget(copy_button)

    def _generate(self) -> None:
        try:
            payload = json.loads(self._payload_input.toPlainText())
        except json.JSONDecodeError as exc:
            self._status_label.setText(f"Invalid JSON payload: {exc.msg}")
            self._output.clear()
            return
        if not isinstance(payload, dict):
            self._status_label.setText("Payload must be a JSON object")
            self._output.clear()
            return

        try:
            token = encode_jwt(
                payload, self._secret_edit.text(), self._algorithm_combo.currentText()
            )
        except ValidationError as exc:
            self._status_label.setText(exc.message)
            self._output.clear()
            return

        self._status_label.setText("")
        self._output.setPlainText(token)
        show_toast(self, "Token generated", "success")

    def _copy_output(self) -> None:
        text = self._output.toPlainText()
        if not text:
            show_toast(self, "Nothing to copy", "warning")
            return
        self.copy_to_clipboard(text)
        show_toast(self, "Copied to clipboard", "success")
