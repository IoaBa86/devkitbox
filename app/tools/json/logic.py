"""Pure JSON formatting/validation logic — no Qt imports, fully unit-testable."""

from __future__ import annotations

import json

from app.core.exceptions import ValidationError


def _wrap_decode_error(exc: json.JSONDecodeError) -> ValidationError:
    return ValidationError(
        "Invalid JSON",
        line=exc.lineno,
        column=exc.colno,
        detail=exc.msg,
    )


def parse_json(text: str) -> object:
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise _wrap_decode_error(exc) from exc


def format_json(text: str, indent: int = 2, sort_keys: bool = False) -> str:
    data = parse_json(text)
    return json.dumps(data, indent=indent, sort_keys=sort_keys, ensure_ascii=False)


def minify_json(text: str) -> str:
    data = parse_json(text)
    return json.dumps(data, separators=(",", ":"), sort_keys=False, ensure_ascii=False)


def validate_json(text: str) -> None:
    """Raises ValidationError if invalid. Returns None when valid."""
    parse_json(text)
