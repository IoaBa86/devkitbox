"""Pure SQL formatting logic — no Qt imports, fully unit-testable.

Wraps ``sqlparse``, a lenient tokenizer/formatter (not a real SQL parser —
it won't catch semantic errors, only re-layouts what it's given).
"""

from __future__ import annotations

import sqlparse

from app.core.exceptions import ValidationError

KEYWORD_CASES = ("upper", "lower", "capitalize")


def format_sql(
    text: str, keyword_case: str = "upper", indent_width: int = 2, strip_comments: bool = False
) -> str:
    if not text.strip():
        raise ValidationError("Enter a SQL statement")
    if keyword_case not in KEYWORD_CASES:
        raise ValidationError(f"Unknown keyword case: {keyword_case}")

    return sqlparse.format(
        text,
        reindent=True,
        keyword_case=keyword_case,
        indent_width=indent_width,
        strip_comments=strip_comments,
    ).strip()


def minify_sql(text: str) -> str:
    if not text.strip():
        raise ValidationError("Enter a SQL statement")

    return sqlparse.format(
        text,
        reindent=False,
        strip_comments=True,
        strip_whitespace=True,
    ).strip()
