from __future__ import annotations

import datetime

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from app.core.exceptions import ValidationError
from app.tools.certdecoder.logic import parse_certificate


def _make_cert(
    common_name: str = "example.com",
    days_valid: int = 30,
    sans: list[str] | None = None,
    self_signed: bool = True,
) -> str:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])
    issuer = (
        subject if self_signed else x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Some CA")])
    )

    builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=60))
        .not_valid_after(datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=days_valid))
    )
    if sans:
        builder = builder.add_extension(
            x509.SubjectAlternativeName([x509.DNSName(s) for s in sans]), critical=False
        )
    cert = builder.sign(key, hashes.SHA256())
    return cert.public_bytes(serialization.Encoding.PEM).decode("ascii")


def test_parse_certificate_basic_fields():
    pem = _make_cert("example.com")
    info = parse_certificate(pem)
    assert info.subject == "example.com"
    assert info.issuer == "example.com"
    assert info.is_self_signed is True
    assert info.is_expired is False


def test_parse_certificate_expired():
    pem = _make_cert("expired.com", days_valid=-10)
    info = parse_certificate(pem)
    assert info.is_expired is True


def test_parse_certificate_not_self_signed():
    pem = _make_cert("leaf.com", self_signed=False)
    info = parse_certificate(pem)
    assert info.is_self_signed is False
    assert info.issuer == "Some CA"


def test_parse_certificate_subject_alternative_names():
    pem = _make_cert("example.com", sans=["example.com", "www.example.com"])
    info = parse_certificate(pem)
    assert set(info.subject_alternative_names) == {"example.com", "www.example.com"}


def test_parse_certificate_no_sans():
    pem = _make_cert("example.com")
    info = parse_certificate(pem)
    assert info.subject_alternative_names == []


def test_parse_certificate_public_key_info():
    pem = _make_cert("example.com")
    info = parse_certificate(pem)
    assert info.public_key_type == "RSA"
    assert info.public_key_size == 2048


def test_parse_certificate_fingerprint_is_hex_pairs():
    pem = _make_cert("example.com")
    info = parse_certificate(pem)
    parts = info.sha256_fingerprint.split(":")
    assert len(parts) == 32
    assert all(len(p) == 2 for p in parts)


def test_parse_certificate_empty_raises():
    with pytest.raises(ValidationError):
        parse_certificate("")


def test_parse_certificate_not_pem_raises():
    with pytest.raises(ValidationError):
        parse_certificate("this is not a certificate")


def test_parse_certificate_malformed_pem_raises():
    with pytest.raises(ValidationError):
        parse_certificate("-----BEGIN CERTIFICATE-----\nnotbase64\n-----END CERTIFICATE-----")
