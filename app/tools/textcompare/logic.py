"""Pure text-diff logic — no Qt imports, fully unit-testable."""

from __future__ import annotations

import difflib
from dataclasses import dataclass

_TAG_LABEL = {
    "equal": " ",
    "replace": "~",
    "delete": "-",
    "insert": "+",
}


@dataclass(frozen=True, slots=True)
class DiffLine:
    marker: str
    text: str


def similarity_ratio(left: str, right: str) -> float:
    return difflib.SequenceMatcher(None, left, right).ratio()


def unified_diff(
    left: str, right: str, left_label: str = "left", right_label: str = "right"
) -> str:
    left_lines = left.splitlines(keepends=True)
    right_lines = right.splitlines(keepends=True)
    diff = difflib.unified_diff(left_lines, right_lines, fromfile=left_label, tofile=right_label)
    return "".join(diff)


def line_diff(left: str, right: str) -> list[DiffLine]:
    left_lines = left.splitlines()
    right_lines = right.splitlines()
    matcher = difflib.SequenceMatcher(None, left_lines, right_lines)

    result: list[DiffLine] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal" or tag == "delete":
            for line in left_lines[i1:i2]:
                result.append(DiffLine(_TAG_LABEL[tag], line))
        elif tag == "insert":
            for line in right_lines[j1:j2]:
                result.append(DiffLine(_TAG_LABEL[tag], line))
        elif tag == "replace":
            for line in left_lines[i1:i2]:
                result.append(DiffLine("-", line))
            for line in right_lines[j1:j2]:
                result.append(DiffLine("+", line))
    return result


def diff_stats(left: str, right: str) -> tuple[int, int, int]:
    lines = line_diff(left, right)
    added = sum(1 for line in lines if line.marker == "+")
    removed = sum(1 for line in lines if line.marker == "-")
    unchanged = sum(1 for line in lines if line.marker == " ")
    return added, removed, unchanged
