"""Pure Base64 encode/decode logic — no Qt imports, fully unit-testable."""

from __future__ import annotations

import base64
import binascii

from app.core.exceptions import ValidationError


def encode_text(text: str, url_safe: bool = False) -> str:
    data = text.encode("utf-8")
    encoded = base64.urlsafe_b64encode(data) if url_safe else base64.b64encode(data)
    return encoded.decode("ascii")


def decode_text(data: str, url_safe: bool = False) -> str:
    try:
        decoder = base64.urlsafe_b64decode if url_safe else base64.b64decode
        raw = decoder(_pad(data))
        return raw.decode("utf-8")
    except (binascii.Error, ValueError) as exc:
        raise ValidationError("Invalid Base64 input", detail=str(exc)) from exc
    except UnicodeDecodeError as exc:
        raise ValidationError(
            "Decoded data is not valid UTF-8 text",
            detail=str(exc),
        ) from exc


def encode_bytes(data: bytes, url_safe: bool = False) -> str:
    encoded = base64.urlsafe_b64encode(data) if url_safe else base64.b64encode(data)
    return encoded.decode("ascii")


def decode_to_bytes(data: str, url_safe: bool = False) -> bytes:
    try:
        decoder = base64.urlsafe_b64decode if url_safe else base64.b64decode
        return decoder(_pad(data))
    except (binascii.Error, ValueError) as exc:
        raise ValidationError("Invalid Base64 input", detail=str(exc)) from exc


def _pad(data: str) -> str:
    stripped = data.strip()
    remainder = len(stripped) % 4
    if remainder:
        stripped += "=" * (4 - remainder)
    return stripped
