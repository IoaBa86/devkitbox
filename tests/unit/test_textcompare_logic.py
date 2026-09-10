from __future__ import annotations

from app.tools.textcompare.logic import diff_stats, line_diff, similarity_ratio, unified_diff


def test_similarity_ratio_identical():
    assert similarity_ratio("abc", "abc") == 1.0


def test_similarity_ratio_completely_different():
    assert similarity_ratio("abc", "xyz") == 0.0


def test_similarity_ratio_partial():
    ratio = similarity_ratio("hello world", "hello there")
    assert 0.0 < ratio < 1.0


def test_line_diff_detects_insert_and_delete():
    left = "a\nb\nc"
    right = "a\nb\nc\nd"
    lines = line_diff(left, right)
    markers = [line.marker for line in lines]
    assert markers == [" ", " ", " ", "+"]
    assert lines[-1].text == "d"


def test_line_diff_detects_replace():
    left = "a\nb\nc"
    right = "a\nx\nc"
    lines = line_diff(left, right)
    assert [(line.marker, line.text) for line in lines] == [
        (" ", "a"),
        ("-", "b"),
        ("+", "x"),
        (" ", "c"),
    ]


def test_diff_stats_counts():
    left = "a\nb\nc"
    right = "a\nx\nc\nd"
    added, removed, unchanged = diff_stats(left, right)
    assert added == 2
    assert removed == 1
    assert unchanged == 2


def test_unified_diff_contains_markers():
    result = unified_diff("a\nb\n", "a\nc\n")
    assert "-b" in result
    assert "+c" in result
