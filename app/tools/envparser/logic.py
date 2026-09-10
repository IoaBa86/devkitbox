"""Pure .env file parsing/validation logic — no Qt imports, fully unit-testable."""

from __future__ import annotations

import re
from dataclasses import dataclass

_LINE_RE = re.compile(r"^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$")


@dataclass(frozen=True, slots=True)
class EnvEntry:
    line_number: int
    key: str
    value: str


@dataclass(frozen=True, slots=True)
class EnvIssue:
    line_number: int | None
    message: str


def _strip_value(raw: str) -> str:
    value = raw.strip()
    # Strip a trailing, unquoted comment (e.g. "value  # comment").
    if value and value[0] not in ("'", '"'):
        comment_index = value.find(" #")
        if comment_index != -1:
            value = value[:comment_index].strip()

    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def parse_env(text: str) -> list[EnvEntry]:
    entries: list[EnvEntry] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = _LINE_RE.match(line)
        if not match:
            continue
        key, raw_value = match.groups()
        entries.append(EnvEntry(line_number=line_number, key=key, value=_strip_value(raw_value)))
    return entries


def to_dict(entries: list[EnvEntry]) -> dict[str, str]:
    return {entry.key: entry.value for entry in entries}


def find_malformed_lines(text: str) -> list[EnvIssue]:
    issues: list[EnvIssue] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if not _LINE_RE.match(line):
            issues.append(EnvIssue(line_number, f"Not a valid KEY=VALUE line: {raw_line!r}"))
    return issues


def validate_env(text: str, required_keys: list[str] | None = None) -> list[EnvIssue]:
    entries = parse_env(text)
    issues = find_malformed_lines(text)

    seen: dict[str, int] = {}
    for entry in entries:
        if entry.key in seen:
            issues.append(
                EnvIssue(
                    entry.line_number,
                    f"Duplicate key {entry.key!r} (first set on line {seen[entry.key]})",
                )
            )
        else:
            seen[entry.key] = entry.line_number
        if entry.value == "":
            issues.append(EnvIssue(entry.line_number, f"{entry.key!r} has an empty value"))

    if required_keys:
        present = to_dict(entries)
        for key in required_keys:
            if key not in present:
                issues.append(EnvIssue(None, f"Missing required key: {key!r}"))

    return issues
