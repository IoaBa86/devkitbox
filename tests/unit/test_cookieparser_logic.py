from __future__ import annotations

import pytest

from app.core.exceptions import ValidationError
from app.tools.cookieparser.logic import parse_cookie_header, parse_set_cookie


def test_parse_set_cookie_basic():
    info = parse_set_cookie("session_id=abc123")
    assert info.name == "session_id"
    assert info.value == "abc123"
    assert info.secure is False
    assert info.http_only is False


def test_parse_set_cookie_full_attributes():
    info = parse_set_cookie(
        "session_id=abc123; Domain=example.com; Path=/; Secure; HttpOnly; SameSite=Lax; Max-Age=3600"
    )
    assert info.domain == "example.com"
    assert info.path == "/"
    assert info.secure is True
    assert info.http_only is True
    assert info.same_site == "Lax"
    assert info.max_age == "3600"


def test_parse_set_cookie_expires():
    info = parse_set_cookie("id=1; Expires=Wed, 21 Oct 2026 07:28:00 GMT")
    assert info.expires == "Wed, 21 Oct 2026 07:28:00 GMT"


def test_parse_set_cookie_case_insensitive_attribute_names():
    info = parse_set_cookie("id=1; DOMAIN=example.com; secure")
    assert info.domain == "example.com"
    assert info.secure is True


def test_parse_set_cookie_unknown_attribute_kept_as_extra():
    info = parse_set_cookie("id=1; Priority=High")
    assert info.attributes == {"Priority": "High"}


def test_parse_set_cookie_empty_raises():
    with pytest.raises(ValidationError):
        parse_set_cookie("")


def test_parse_set_cookie_missing_equals_raises():
    with pytest.raises(ValidationError):
        parse_set_cookie("not-a-cookie")


def test_parse_set_cookie_value_with_equals_sign():
    info = parse_set_cookie("token=abc=def")
    assert info.value == "abc=def"


def test_parse_cookie_header_multiple_cookies():
    result = parse_cookie_header("session_id=abc123; theme=dark; lang=en")
    assert result == {"session_id": "abc123", "theme": "dark", "lang": "en"}


def test_parse_cookie_header_empty():
    assert parse_cookie_header("") == {}


def test_parse_cookie_header_ignores_malformed_segments():
    result = parse_cookie_header("valid=1; malformed; also_valid=2")
    assert result == {"valid": "1", "also_valid": "2"}
