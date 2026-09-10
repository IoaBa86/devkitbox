from __future__ import annotations

import pytest

from app.core.exceptions import ValidationError
from app.tools.json.logic import format_json, minify_json, validate_json


def test_format_json_pretty_prints_with_indent():
    result = format_json('{"b": 1, "a": 2}', indent=2, sort_keys=False)
    assert result == '{\n  "b": 1,\n  "a": 2\n}'


def test_format_json_sort_keys():
    result = format_json('{"b": 1, "a": 2}', indent=2, sort_keys=True)
    assert result.index('"a"') < result.index('"b"')


def test_minify_json_removes_whitespace():
    result = minify_json('{\n  "a": 1,\n  "b": [1, 2, 3]\n}')
    assert result == '{"a":1,"b":[1,2,3]}'


def test_validate_json_valid_returns_none():
    assert validate_json('{"a": 1}') is None


def test_invalid_json_raises_validation_error_with_location():
    with pytest.raises(ValidationError) as exc_info:
        format_json('{"a": 1,}')
    error = exc_info.value
    assert error.line is not None
    assert error.column is not None


def test_empty_input_raises_validation_error():
    with pytest.raises(ValidationError):
        validate_json("")
