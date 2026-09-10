"""Pure line-manipulation logic — no Qt imports, fully unit-testable."""

from __future__ import annotations

import random


def sort_ascending(text: str) -> str:
    return "\n".join(sorted(text.splitlines()))


def sort_descending(text: str) -> str:
    return "\n".join(sorted(text.splitlines(), reverse=True))


def remove_duplicates(text: str) -> str:
    seen: set[str] = set()
    result = []
    for line in text.splitlines():
        if line not in seen:
            seen.add(line)
            result.append(line)
    return "\n".join(result)


def remove_empty_lines(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if line.strip())


def trim_lines(text: str) -> str:
    return "\n".join(line.strip() for line in text.splitlines())


def reverse_lines(text: str) -> str:
    return "\n".join(reversed(text.splitlines()))


def shuffle_lines(text: str) -> str:
    lines = text.splitlines()
    random.shuffle(lines)
    return "\n".join(lines)


def add_line_numbers(text: str) -> str:
    lines = text.splitlines()
    width = len(str(len(lines)))
    return "\n".join(f"{i + 1:>{width}}. {line}" for i, line in enumerate(lines))
