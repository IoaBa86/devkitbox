"""Pure X.509 certificate decoding logic — no Qt imports, fully unit-testable.

Inspection only — never verifies a chain, never checks revocation, and
never touches the network. Parsing is entirely local/offline.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.x509.oid import NameOID

from app.core.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class CertificateInfo:
    subject: str
    issuer: str
    serial_number: str
    version: str
    not_before: datetime
    not_after: datetime
    is_expired: bool
    is_self_signed: bool
    signature_algorithm: str
    public_key_type: str
    public_key_size: int | None
    subject_alternative_names: list[str]
    sha256_fingerprint: str


def _name_to_str(name: x509.Name) -> str:
    common_name = name.get_attributes_for_oid(NameOID.COMMON_NAME)
    if common_name:
        return common_name[0].value
    return name.rfc4514_string()


def _public_key_info(cert: x509.Certificate) -> tuple[str, int | None]:
    public_key = cert.public_key()
    key_type = type(public_key).__name__.lstrip("_").removesuffix("PublicKey")
    key_size = getattr(public_key, "key_size", None)
    return key_type, key_size


def parse_certificate(pem_text: str) -> CertificateInfo:
    text = pem_text.strip()
    if not text:
        raise ValidationError("Paste a PEM-encoded certificate")
    if "BEGIN CERTIFICATE" not in text:
        raise ValidationError("Expected a PEM certificate (-----BEGIN CERTIFICATE-----)")

    try:
        cert = x509.load_pem_x509_certificate(text.encode("utf-8"))
    except ValueError as exc:
        raise ValidationError("Could not parse certificate", detail=str(exc)) from exc

    try:
        sans = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        san_values = [str(name.value) for name in sans.value]
    except x509.ExtensionNotFound:
        san_values = []

    key_type, key_size = _public_key_info(cert)
    not_after = cert.not_valid_after_utc
    not_before = cert.not_valid_before_utc

    return CertificateInfo(
        subject=_name_to_str(cert.subject),
        issuer=_name_to_str(cert.issuer),
        serial_number=format(cert.serial_number, "x"),
        version=str(cert.version.name),
        not_before=not_before,
        not_after=not_after,
        is_expired=datetime.now(UTC) > not_after,
        is_self_signed=cert.subject == cert.issuer,
        signature_algorithm=cert.signature_algorithm_oid._name,
        public_key_type=key_type,
        public_key_size=key_size,
        subject_alternative_names=san_values,
        sha256_fingerprint=cert.fingerprint(hashes.SHA256()).hex(":").upper(),
    )
