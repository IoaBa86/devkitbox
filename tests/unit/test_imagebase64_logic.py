from __future__ import annotations

import base64

import pytest

from app.core.exceptions import ValidationError
from app.tools.imagebase64.logic import (
    decode_image_base64,
    detect_image_format,
    encode_image_to_data_uri,
    format_byte_size,
    strip_data_uri_prefix,
)

# A real, minimal 1x1 transparent PNG.
_PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)
_PNG_B64 = base64.b64encode(_PNG_BYTES).decode("ascii")


def test_strip_data_uri_prefix_with_prefix():
    mime, payload = strip_data_uri_prefix(f"data:image/png;base64,{_PNG_B64}")
    assert mime == "image/png"
    assert payload == _PNG_B64


def test_strip_data_uri_prefix_without_prefix():
    mime, payload = strip_data_uri_prefix(_PNG_B64)
    assert mime is None
    assert payload == _PNG_B64


def test_decode_image_base64_from_raw():
    assert decode_image_base64(_PNG_B64) == _PNG_BYTES


def test_decode_image_base64_from_data_uri():
    assert decode_image_base64(f"data:image/png;base64,{_PNG_B64}") == _PNG_BYTES


def test_decode_image_base64_invalid_raises():
    with pytest.raises(ValidationError):
        decode_image_base64("not valid base64!!!")


def test_detect_image_format_png():
    assert detect_image_format(_PNG_BYTES) == "PNG"


def test_detect_image_format_jpeg():
    assert detect_image_format(b"\xff\xd8\xff\xe0rest") == "JPEG"


def test_detect_image_format_unknown():
    assert detect_image_format(b"not an image") == "Unknown"


def test_encode_image_to_data_uri_detects_mime():
    uri = encode_image_to_data_uri(_PNG_BYTES)
    assert uri.startswith("data:image/png;base64,")
    assert uri.endswith(_PNG_B64)


def test_encode_image_to_data_uri_explicit_mime():
    uri = encode_image_to_data_uri(_PNG_BYTES, "image/x-custom")
    assert uri.startswith("data:image/x-custom;base64,")


def test_encode_decode_round_trip():
    uri = encode_image_to_data_uri(_PNG_BYTES)
    assert decode_image_base64(uri) == _PNG_BYTES


def test_format_byte_size_bytes():
    assert format_byte_size(500) == "500 B"


def test_format_byte_size_kilobytes():
    assert format_byte_size(2048) == "2.00 KB"
