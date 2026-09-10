from __future__ import annotations

from app.tools.markdown.logic import Heading, build_toc, extract_headings, word_count


def test_extract_headings_various_levels():
    text = "# Title\n\n## Section One\n\nSome text.\n\n### Sub Section\n"
    headings = extract_headings(text)
    assert headings == [
        Heading(level=1, title="Title", slug="title"),
        Heading(level=2, title="Section One", slug="section-one"),
        Heading(level=3, title="Sub Section", slug="sub-section"),
    ]


def test_extract_headings_no_headings():
    assert extract_headings("just some text\nno headings here") == []


def test_extract_headings_ignores_non_heading_hash():
    assert extract_headings("this is #not a heading") == []


def test_build_toc_indents_by_level():
    headings = [
        Heading(level=1, title="Intro", slug="intro"),
        Heading(level=2, title="Details", slug="details"),
    ]
    toc = build_toc(headings)
    assert toc == "- [Intro](#intro)\n  - [Details](#details)"


def test_build_toc_empty():
    assert build_toc([]) == ""


def test_word_count():
    assert word_count("hello world  foo\nbar") == 4


def test_word_count_empty():
    assert word_count("") == 0
