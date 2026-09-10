from __future__ import annotations

import pytest

from app.core.exceptions import ValidationError
from app.tools.base64.logic import decode_text, decode_to_bytes, encode_bytes, encode_text


def test_encode_text_known_vector():
    assert encode_text("hello") == "aGVsbG8="


def test_roundtrip_text():
    original = "The quick brown fox! 🦊"
    assert decode_text(encode_text(original)) == original


def test_url_safe_roundtrip():
    original = "?data=a b/c+d"
    encoded = encode_text(original, url_safe=True)
    assert "+" not in encoded and "/" not in encoded
    assert decode_text(encoded, url_safe=True) == original


def test_decode_invalid_base64_raises():
    with pytest.raises(ValidationError):
        decode_text("not-valid-base64!!!")


def test_decode_handles_missing_padding():
    encoded = encode_text("abc").rstrip("=")
    assert decode_text(encoded) == "abc"


def test_bytes_roundtrip():
    data = bytes(range(256))
    assert decode_to_bytes(encode_bytes(data)) == data
