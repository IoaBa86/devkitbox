from __future__ import annotations

from app.tools.envparser.logic import find_malformed_lines, parse_env, to_dict, validate_env


def test_parse_env_basic():
    entries = parse_env("FOO=bar\nBAZ=qux")
    assert [(e.key, e.value) for e in entries] == [("FOO", "bar"), ("BAZ", "qux")]


def test_parse_env_skips_comments_and_blank_lines():
    entries = parse_env("# comment\n\nFOO=bar\n  # another\n")
    assert [(e.key, e.value) for e in entries] == [("FOO", "bar")]


def test_parse_env_strips_double_quotes():
    entries = parse_env('FOO="hello world"')
    assert entries[0].value == "hello world"


def test_parse_env_strips_single_quotes():
    entries = parse_env("FOO='hello world'")
    assert entries[0].value == "hello world"


def test_parse_env_strips_inline_comment_on_unquoted_value():
    entries = parse_env("FOO=bar # this is a comment")
    assert entries[0].value == "bar"


def test_parse_env_preserves_hash_inside_quoted_value():
    entries = parse_env('FOO="bar#baz"')
    assert entries[0].value == "bar#baz"


def test_parse_env_export_prefix():
    entries = parse_env("export FOO=bar")
    assert entries[0].key == "FOO"
    assert entries[0].value == "bar"


def test_parse_env_empty_value():
    entries = parse_env("FOO=")
    assert entries[0].value == ""


def test_parse_env_line_numbers():
    entries = parse_env("# comment\nFOO=bar\n\nBAZ=qux")
    assert entries[0].line_number == 2
    assert entries[1].line_number == 4


def test_to_dict():
    entries = parse_env("FOO=bar\nBAZ=qux")
    assert to_dict(entries) == {"FOO": "bar", "BAZ": "qux"}


def test_find_malformed_lines():
    issues = find_malformed_lines("FOO=bar\nnot a valid line\nBAZ=qux")
    assert len(issues) == 1
    assert issues[0].line_number == 2


def test_validate_env_detects_duplicate_keys():
    issues = validate_env("FOO=bar\nFOO=baz")
    messages = [i.message for i in issues]
    assert any("Duplicate key" in m for m in messages)


def test_validate_env_detects_empty_value():
    issues = validate_env("FOO=")
    assert any("empty value" in i.message for i in issues)


def test_validate_env_detects_missing_required_key():
    issues = validate_env("FOO=bar", required_keys=["FOO", "BAZ"])
    assert any("BAZ" in i.message for i in issues)
    assert not any("FOO" in i.message and "Missing" in i.message for i in issues)


def test_validate_env_no_issues_for_clean_input():
    assert validate_env("FOO=bar\nBAZ=qux", required_keys=["FOO"]) == []
