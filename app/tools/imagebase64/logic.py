"""Pure image<->Base64 logic — no Qt imports, fully unit-testable.

Actual image *decoding* (turning bytes into pixels) is left to Qt's
QPixmap in the widget — this module only handles the Base64/data-URI
text layer and magic-byte format sniffing.
"""

from __future__ import annotations

import re

from app.tools.base64.logic import decode_to_bytes, encode_bytes

_DATA_URI_RE = re.compile(r"^data:([\w./+-]+);base64,(.*)$", re.DOTALL)

_MAGIC_BYTES: tuple[tuple[bytes, str, str], ...] = (
    (b"\x89PNG\r\n\x1a\n", "PNG", "image/png"),
    (b"\xff\xd8\xff", "JPEG", "image/jpeg"),
    (b"GIF87a", "GIF", "image/gif"),
    (b"GIF89a", "GIF", "image/gif"),
    (b"BM", "BMP", "image/bmp"),
    (b"RIFF", "WEBP", "image/webp"),  # RIFF....WEBP; good enough for a sniff
)


def strip_data_uri_prefix(text: str) -> tuple[str | None, str]:
    """Return (mime_type, base64_payload). mime_type is None for raw base64."""
    match = _DATA_URI_RE.match(text.strip())
    if match:
        return match.group(1), match.group(2)
    return None, text.strip()


def decode_image_base64(text: str) -> bytes:
    _mime, payload = strip_data_uri_prefix(text)
    return decode_to_bytes(payload)


def detect_image_format(data: bytes) -> str:
    for magic, name, _mime in _MAGIC_BYTES:
        if data.startswith(magic):
            return name
    return "Unknown"


def encode_image_to_data_uri(data: bytes, mime_type: str | None = None) -> str:
    if mime_type is None:
        fmt = detect_image_format(data)
        mime_type = next((mime for _magic, name, mime in _MAGIC_BYTES if name == fmt), None)
        mime_type = mime_type or "application/octet-stream"
    return f"data:{mime_type};base64,{encode_bytes(data)}"


def format_byte_size(size_bytes: int) -> str:
    size = float(size_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.2f} {unit}" if unit != "B" else f"{int(size)} {unit}"
        size /= 1024
    return f"{size:.2f} GB"
