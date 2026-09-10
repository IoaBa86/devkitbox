from __future__ import annotations

from app.tools.lines.logic import (
    add_line_numbers,
    remove_duplicates,
    remove_empty_lines,
    reverse_lines,
    shuffle_lines,
    sort_ascending,
    sort_descending,
    trim_lines,
)


def test_sort_ascending():
    assert sort_ascending("banana\napple\ncherry") == "apple\nbanana\ncherry"


def test_sort_descending():
    assert sort_descending("banana\napple\ncherry") == "cherry\nbanana\napple"


def test_remove_duplicates_preserves_order():
    assert remove_duplicates("a\nb\na\nc\nb") == "a\nb\nc"


def test_remove_empty_lines():
    assert remove_empty_lines("a\n\n  \nb\n") == "a\nb"


def test_trim_lines():
    assert trim_lines("  a  \n b \n c") == "a\nb\nc"


def test_reverse_lines():
    assert reverse_lines("a\nb\nc") == "c\nb\na"


def test_shuffle_lines_preserves_multiset():
    original = "a\nb\nc\nd\ne"
    result = shuffle_lines(original)
    assert sorted(result.splitlines()) == sorted(original.splitlines())


def test_add_line_numbers():
    assert add_line_numbers("a\nb\nc") == "1. a\n2. b\n3. c"
