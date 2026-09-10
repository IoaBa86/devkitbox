from __future__ import annotations

import pytest

from app.core.exceptions import ValidationError
from app.tools.sqlformat.logic import format_sql, minify_sql


def test_format_sql_uppercases_keywords():
    result = format_sql("select id from users")
    assert "SELECT" in result
    assert "FROM" in result


def test_format_sql_lowercase_keyword_case():
    result = format_sql("SELECT id FROM users", keyword_case="lower")
    assert "select" in result
    assert "SELECT" not in result


def test_format_sql_reindents_multiline():
    result = format_sql("select id, name from users where active = 1")
    assert "\n" in result


def test_format_sql_empty_raises():
    with pytest.raises(ValidationError):
        format_sql("")


def test_format_sql_unknown_case_raises():
    with pytest.raises(ValidationError):
        format_sql("select 1", keyword_case="weird")


def test_format_sql_strip_comments():
    result = format_sql("select 1 -- a comment", strip_comments=True)
    assert "comment" not in result


def test_minify_sql_removes_extra_whitespace():
    result = minify_sql("SELECT   id,   name\nFROM   users")
    assert "\n" not in result
    assert "   " not in result


def test_minify_sql_strips_comments():
    result = minify_sql("SELECT 1 -- comment")
    assert "comment" not in result


def test_minify_sql_empty_raises():
    with pytest.raises(ValidationError):
        minify_sql("")
