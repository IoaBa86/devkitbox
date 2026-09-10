"""Pure text statistics logic — no Qt imports, fully unit-testable."""

from __future__ import annotations

import re
from dataclasses import dataclass

_WORDS_PER_MINUTE = 200


@dataclass(frozen=True, slots=True)
class TextStats:
    characters: int
    characters_no_spaces: int
    words: int
    lines: int
    paragraphs: int
    byte_count: int
    reading_time_minutes: float


def compute_stats(text: str) -> TextStats:
    if not text:
        return TextStats(0, 0, 0, 0, 0, 0, 0.0)

    characters = len(text)
    characters_no_spaces = len(re.sub(r"\s", "", text))
    words = len(text.split())
    lines = text.count("\n") + 1
    paragraphs = len([p for p in re.split(r"\n\s*\n", text) if p.strip()])
    byte_count = len(text.encode("utf-8"))
    reading_time_minutes = words / _WORDS_PER_MINUTE

    return TextStats(
        characters=characters,
        characters_no_spaces=characters_no_spaces,
        words=words,
        lines=lines,
        paragraphs=paragraphs,
        byte_count=byte_count,
        reading_time_minutes=reading_time_minutes,
    )
