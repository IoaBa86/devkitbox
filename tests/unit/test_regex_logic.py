from __future__ import annotations

import pytest

from app.core.exceptions import ValidationError
from app.tools.regex.logic import RegexTimeoutError, compile_pattern, find_matches


def test_find_matches_basic():
    result = find_matches(r"\d+", "a1 b22 c333")
    assert [m.text for m in result.matches] == ["1", "22", "333"]
    assert result.group_count == 0


def test_find_matches_no_matches():
    result = find_matches(r"\d+", "no digits here")
    assert result.matches == []


def test_find_matches_captures_groups():
    result = find_matches(r"(\w+)@(\w+)", "user@host")
    assert result.group_count == 2
    assert result.matches[0].groups == ("user", "host")


def test_find_matches_ignorecase_flag():
    result = find_matches("hello", "HELLO", ["IGNORECASE"])
    assert len(result.matches) == 1


def test_find_matches_without_ignorecase_flag_no_match():
    result = find_matches("hello", "HELLO")
    assert result.matches == []


def test_find_matches_multiline_flag():
    result = find_matches("^b", "a\nb", ["MULTILINE"])
    assert len(result.matches) == 1


def test_compile_pattern_invalid_raises_validation_error():
    with pytest.raises(ValidationError):
        compile_pattern("(unclosed")


def test_find_matches_invalid_pattern_raises_validation_error():
    with pytest.raises(ValidationError):
        find_matches("(unclosed", "text")


def test_find_matches_wraps_timeout_as_validation_error(monkeypatch):
    class _FakeCompiled:
        groups = 0

        def finditer(self, text, timeout=None):
            raise TimeoutError("took too long")

    monkeypatch.setattr("app.tools.regex.logic.compile_pattern", lambda *a, **k: _FakeCompiled())

    with pytest.raises(RegexTimeoutError) as exc_info:
        find_matches(r"(a+)+$", "a" * 100)
    assert "taking too long" in exc_info.value.message


def test_regex_timeout_error_is_a_validation_error():
    assert issubclass(RegexTimeoutError, ValidationError)
