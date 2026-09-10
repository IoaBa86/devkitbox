"""Pure JWT decoding logic — no Qt imports, fully unit-testable.

This decodes a JWT's header and payload for inspection only. It never
verifies the signature, and callers must not present a decoded token as
"valid" — decoding success only means the token is well-formed.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime

from app.core.exceptions import ValidationError

_STANDARD_CLAIMS = ("iss", "sub", "aud", "exp", "nbf", "iat", "jti")

HMAC_ALGORITHMS: dict[str, Callable[[], hashlib._Hash]] = {
    "HS256": hashlib.sha256,
    "HS384": hashlib.sha384,
    "HS512": hashlib.sha512,
}


@dataclass(frozen=True, slots=True)
class JwtResult:
    header: dict
    payload: dict
    signature: str
    issued_at: str | None
    expires_at: str | None
    not_before: str | None
    is_expired: bool | None
    standard_claims: dict[str, str]


def _b64url_decode(segment: str) -> bytes:
    padded = segment + "=" * (-len(segment) % 4)
    try:
        return base64.urlsafe_b64decode(padded)
    except (binascii.Error, ValueError) as exc:
        raise ValidationError("Invalid JWT", detail=str(exc)) from exc


def _decode_json_segment(segment: str, part_name: str) -> dict:
    raw = _b64url_decode(segment)
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValidationError(f"Invalid JWT {part_name}", detail=str(exc)) from exc
    if not isinstance(data, dict):
        raise ValidationError(f"Invalid JWT {part_name}", detail="Expected a JSON object")
    return data


def _format_epoch(value: object) -> str | None:
    if not isinstance(value, int | float):
        return None
    try:
        return datetime.fromtimestamp(value, tz=UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    except (ValueError, OverflowError, OSError):
        return None


def decode_jwt(token: str) -> JwtResult:
    parts = token.strip().split(".")
    if len(parts) != 3:
        raise ValidationError(
            "Invalid JWT",
            detail="Expected 3 dot-separated segments: header.payload.signature",
        )

    header_b64, payload_b64, signature_b64 = parts
    header = _decode_json_segment(header_b64, "header")
    payload = _decode_json_segment(payload_b64, "payload")

    exp = payload.get("exp")
    iat = payload.get("iat")
    nbf = payload.get("nbf")

    is_expired = None
    if isinstance(exp, int | float):
        is_expired = datetime.now(UTC).timestamp() > exp

    standard_claims = {
        key: str(payload[key])
        for key in _STANDARD_CLAIMS
        if key in payload and key not in ("exp", "iat", "nbf")
    }

    return JwtResult(
        header=header,
        payload=payload,
        signature=signature_b64,
        issued_at=_format_epoch(iat),
        expires_at=_format_epoch(exp),
        not_before=_format_epoch(nbf),
        is_expired=is_expired,
        standard_claims=standard_claims,
    )


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def encode_jwt(payload: dict, secret: str, algorithm: str = "HS256") -> str:
    """Build an HMAC-signed (HS256/HS384/HS512) JWT for local testing.

    Only HMAC algorithms are supported — there is no key-pair management
    UI here, and RS/ES algorithms need one.
    """
    if algorithm not in HMAC_ALGORITHMS:
        raise ValidationError(
            f"Unsupported algorithm: {algorithm!r}",
            detail=f"Supported: {', '.join(HMAC_ALGORITHMS)}",
        )
    if not secret:
        raise ValidationError("Enter a secret to sign with")

    header = {"alg": algorithm, "typ": "JWT"}
    try:
        header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
        payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    except TypeError as exc:
        raise ValidationError("Payload is not JSON-serializable", detail=str(exc)) from exc

    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    digestmod = HMAC_ALGORITHMS[algorithm]
    signature = hmac.new(secret.encode("utf-8"), signing_input, digestmod).digest()
    signature_b64 = _b64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{signature_b64}"
