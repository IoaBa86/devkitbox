"""Certificate (X.509) Decoder tool page.

Inspection only — parses a pasted PEM certificate locally. Never contacts
a network, never verifies a chain or checks revocation.
"""

from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from app.core.exceptions import ValidationError
from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.certdecoder.logic import parse_certificate
from app.ui.widgets.code_editor import CodeEditor
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="certificate_decoder",
    name="Certificate Decoder",
    description="Inspect a PEM-encoded X.509 certificate: subject, issuer, validity, SANs.",
    category="Development",
    keywords=("certificate", "x509", "pem", "tls", "ssl", "decoder"),
)

_FIELDS = (
    "Subject",
    "Issuer",
    "Self-Signed",
    "Serial Number",
    "Version",
    "Not Before",
    "Not After",
    "Status",
    "Signature Algorithm",
    "Public Key",
    "SHA-256 Fingerprint",
    "Subject Alternative Names",
)


class CertificateDecoderTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        layout.addWidget(QLabel("PEM CERTIFICATE"))
        self._input = CodeEditor(placeholder="-----BEGIN CERTIFICATE-----\n...")
        self._input.setMaximumHeight(160)
        layout.addWidget(self._input)

        form = QFormLayout()
        self._labels: dict[str, QLabel] = {}
        for field in _FIELDS:
            label = QLabel("—")
            label.setWordWrap(True)
            form.addRow(field, label)
            self._labels[field] = label
        layout.addLayout(form)

        layout.addStretch(1)

    def build_actions(self, layout: QHBoxLayout) -> None:
        decode_button = QPushButton("Decode")
        decode_button.setObjectName("primaryButton")
        decode_button.clicked.connect(self._decode)
        layout.addWidget(decode_button)
        layout.addStretch(1)

        copy_button = QPushButton("Copy Fingerprint")
        copy_button.clicked.connect(self._copy_fingerprint)
        layout.addWidget(copy_button)

    def _decode(self) -> None:
        try:
            info = parse_certificate(self._input.toPlainText())
        except ValidationError as exc:
            show_toast(self, exc.message, "error")
            for label in self._labels.values():
                label.setText("—")
            return

        self._labels["Subject"].setText(info.subject)
        self._labels["Issuer"].setText(info.issuer)
        self._labels["Self-Signed"].setText("Yes" if info.is_self_signed else "No")
        self._labels["Serial Number"].setText(info.serial_number)
        self._labels["Version"].setText(info.version)
        self._labels["Not Before"].setText(info.not_before.strftime("%Y-%m-%d %H:%M:%S UTC"))
        self._labels["Not After"].setText(info.not_after.strftime("%Y-%m-%d %H:%M:%S UTC"))
        self._labels["Status"].setText("Expired" if info.is_expired else "Valid (not expired)")
        self._labels["Signature Algorithm"].setText(info.signature_algorithm)
        key_size = f" ({info.public_key_size} bits)" if info.public_key_size else ""
        self._labels["Public Key"].setText(f"{info.public_key_type}{key_size}")
        self._labels["SHA-256 Fingerprint"].setText(info.sha256_fingerprint)
        self._labels["Subject Alternative Names"].setText(
            ", ".join(info.subject_alternative_names) or "—"
        )
        show_toast(self, "Certificate decoded", "success")

    def _copy_fingerprint(self) -> None:
        text = self._labels["SHA-256 Fingerprint"].text()
        if not text or text == "—":
            show_toast(self, "Nothing to copy", "warning")
            return
        self.copy_to_clipboard(text)
        show_toast(self, "Copied to clipboard", "success")
