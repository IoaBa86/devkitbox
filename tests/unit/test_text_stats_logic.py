from __future__ import annotations

from app.tools.text_stats.logic import compute_stats


def test_compute_stats_empty_text():
    stats = compute_stats("")
    assert stats.characters == 0
    assert stats.words == 0
    assert stats.lines == 0
    assert stats.paragraphs == 0
    assert stats.byte_count == 0
    assert stats.reading_time_minutes == 0.0


def test_compute_stats_basic_counts():
    text = "Hello world\nfoo bar"
    stats = compute_stats(text)
    assert stats.characters == len(text)
    assert stats.words == 4
    assert stats.lines == 2
    assert stats.characters_no_spaces == len("Helloworldfoobar")


def test_compute_stats_paragraphs():
    text = "Para one.\n\nPara two.\n\n\nPara three."
    stats = compute_stats(text)
    assert stats.paragraphs == 3


def test_compute_stats_byte_count_multibyte():
    stats = compute_stats("café")
    assert stats.byte_count == len("café".encode())
    assert stats.characters == 4


def test_compute_stats_reading_time():
    text = " ".join(["word"] * 400)
    stats = compute_stats(text)
    assert stats.reading_time_minutes == 2.0
