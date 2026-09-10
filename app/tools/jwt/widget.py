"""JWT Decoder tool page: inspect header/payload/claims. Never verifies signatures."""

from __future__ import annotations

import json

from PySide6.QtWidgets import QFormLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from app.core.exceptions import ValidationError
from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.jwt.logic import decode_jwt
from app.ui.widgets.code_editor import CodeEditor
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="jwt_decoder",
    name="JWT Decoder",
    description="Decode tokens and inspect claims. Does not verify signatures.",
    category="Development",
    keywords=("jwt", "json web token", "decode", "claims", "auth"),
)


class JwtDecoderTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        layout.addWidget(QLabel("Paste a JWT"))
        self._input = CodeEditor(placeholder="eyJhbGciOi...")
        self._input.setMaximumHeight(80)
        self._input.textChanged.connect(self._on_text_changed)
        layout.addWidget(self._input)

        warning = QLabel("⚠ Decoding a JWT does not verify its signature.")
        warning.setStyleSheet("color: #E8A93B; font-weight: 600;")
        layout.addWidget(warning)

        self._status_label = QLabel("")
        self._status_label.setObjectName("toolDescription")
        layout.addWidget(self._status_label)

        panes = QHBoxLayout()
        panes.setSpacing(12)

        header_col = QVBoxLayout()
        header_col.addWidget(QLabel("HEADER"))
        self._header_view = CodeEditor(read_only=True)
        header_col.addWidget(self._header_view)
        panes.addLayout(header_col)

        payload_col = QVBoxLayout()
        payload_col.addWidget(QLabel("PAYLOAD"))
        self._payload_view = CodeEditor(read_only=True)
        payload_col.addWidget(self._payload_view)
        panes.addLayout(payload_col)

        layout.addLayout(panes, stretch=1)

        layout.addWidget(QLabel("SIGNATURE (unverified)"))
        self._signature_view = CodeEditor(read_only=True)
        self._signature_view.setMaximumHeight(60)
        layout.addWidget(self._signature_view)

        claims_form = QFormLayout()
        self._issued_at_label = QLabel("—")
        self._expires_at_label = QLabel("—")
        self._not_before_label = QLabel("—")
        self._expired_label = QLabel("—")
        claims_form.addRow("Issued at", self._issued_at_label)
        claims_form.addRow("Expires at", self._expires_at_label)
        claims_form.addRow("Not before", self._not_before_label)
        claims_form.addRow("Status", self._expired_label)
        layout.addLayout(claims_form)

    def build_actions(self, layout: QHBoxLayout) -> None:
        decode_button = QPushButton("Decode")
        decode_button.setObjectName("primaryButton")
        decode_button.clicked.connect(lambda: self._decode(announce=True))
        layout.addWidget(decode_button)
        layout.addStretch(1)

        copy_button = QPushButton("Copy Payload")
        copy_button.clicked.connect(self._copy_payload)
        layout.addWidget(copy_button)

    def _on_text_changed(self) -> None:
        self._decode(announce=False)

    def _decode(self, announce: bool) -> None:
        token = self._input.toPlainText().strip()
        if not token:
            self._clear_outputs()
            return
        try:
            result = decode_jwt(token)
        except ValidationError as exc:
            self._clear_outputs()
            self._status_label.setText(exc.message)
            if announce:
                show_toast(self, exc.message, "error")
            return

        self._status_label.setText("")
        self._header_view.setPlainText(json.dumps(result.header, indent=2))
        self._payload_view.setPlainText(json.dumps(result.payload, indent=2))
        self._signature_view.setPlainText(result.signature)
        self._issued_at_label.setText(result.issued_at or "—")
        self._expires_at_label.setText(result.expires_at or "—")
        self._not_before_label.setText(result.not_before or "—")

        if result.is_expired is None:
            self._expired_label.setText("No expiration claim")
        elif result.is_expired:
            self._expired_label.setText("Expired")
        else:
            self._expired_label.setText("Not expired")

        if announce:
            show_toast(self, "Token decoded", "success")

    def _clear_outputs(self) -> None:
        self._header_view.clear()
        self._payload_view.clear()
        self._signature_view.clear()
        self._issued_at_label.setText("—")
        self._expires_at_label.setText("—")
        self._not_before_label.setText("—")
        self._expired_label.setText("—")

    def _copy_payload(self) -> None:
        text = self._payload_view.toPlainText()
        if not text:
            show_toast(self, "Nothing to copy", "warning")
            return
        self.copy_to_clipboard(text)
        show_toast(self, "Copied to clipboard", "success")
