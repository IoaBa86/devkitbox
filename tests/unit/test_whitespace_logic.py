from __future__ import annotations

from app.tools.whitespace.logic import (
    clean_all,
    collapse_blank_lines,
    collapse_spaces,
    ensure_trailing_newline,
    normalize_line_endings,
    remove_blank_lines,
    spaces_to_tabs,
    tabs_to_spaces,
    trim_leading_trailing,
    trim_trailing_whitespace,
)


def test_normalize_line_endings_crlf_and_cr():
    assert normalize_line_endings("a\r\nb\rc") == "a\nb\nc"


def test_trim_trailing_whitespace():
    assert trim_trailing_whitespace("a   \nb\t\nc") == "a\nb\nc"


def test_trim_leading_trailing():
    assert trim_leading_trailing("  a  \n b \n c") == "a\nb\nc"


def test_collapse_spaces_multiple_runs():
    assert collapse_spaces("a    b\tc   d") == "a b\tc d"


def test_collapse_blank_lines():
    assert collapse_blank_lines("a\n\n\n\nb") == "a\n\nb"


def test_remove_blank_lines():
    assert remove_blank_lines("a\n\n  \nb") == "a\nb"


def test_tabs_to_spaces():
    assert tabs_to_spaces("\ta", tab_size=4) == "    a"


def test_spaces_to_tabs():
    assert spaces_to_tabs("    a", tab_size=4) == "\ta"


def test_spaces_to_tabs_no_match_unchanged():
    assert spaces_to_tabs("  a", tab_size=4) == "  a"


def test_ensure_trailing_newline_adds():
    assert ensure_trailing_newline("a") == "a\n"


def test_ensure_trailing_newline_noop_when_present():
    assert ensure_trailing_newline("a\n") == "a\n"


def test_ensure_trailing_newline_empty():
    assert ensure_trailing_newline("") == ""


def test_clean_all_combines_steps():
    result = clean_all("a  \r\n\n\n\nb\t")
    assert result == "a\n\nb\n"
