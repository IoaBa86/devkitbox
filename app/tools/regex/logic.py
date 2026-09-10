"""Pure regex testing logic — no Qt imports, fully unit-testable.

Uses the third-party ``regex`` package rather than stdlib ``re``: it exposes
a real ``timeout`` that interrupts matching at the C level, which stdlib
``re`` cannot do — a catastrophic-backtracking pattern (e.g. ``(a+)+$``)
runs unboundedly in ``re`` regardless of which thread calls it, because
CPython's GIL means a "background thread" doesn't rescue the caller.
"""

from __future__ import annotations

from dataclasses import dataclass

import regex

from app.core.exceptions import ValidationError

FLAGS: dict[str, regex.RegexFlag] = {
    "IGNORECASE": regex.IGNORECASE,
    "MULTILINE": regex.MULTILINE,
    "DOTALL": regex.DOTALL,
    "VERBOSE": regex.VERBOSE,
}

_MATCH_TIMEOUT_SECONDS = 2.0


class RegexTimeoutError(ValidationError):
    """Raised when matching doesn't finish within the timeout budget."""


@dataclass(frozen=True, slots=True)
class MatchDetail:
    index: int
    text: str
    start: int
    end: int
    groups: tuple[str | None, ...]


@dataclass(frozen=True, slots=True)
class RegexResult:
    matches: list[MatchDetail]
    group_count: int


def _combine_flags(flag_names: list[str]) -> regex.RegexFlag:
    combined = regex.RegexFlag(0)
    for name in flag_names:
        combined |= FLAGS[name]
    return combined


def compile_pattern(pattern: str, flag_names: list[str] | None = None) -> regex.Pattern:
    try:
        return regex.compile(pattern, _combine_flags(flag_names or []))
    except regex.error as exc:
        raise ValidationError("Invalid regular expression", detail=str(exc)) from exc


def find_matches(pattern: str, text: str, flag_names: list[str] | None = None) -> RegexResult:
    compiled = compile_pattern(pattern, flag_names)
    try:
        found = list(compiled.finditer(text, timeout=_MATCH_TIMEOUT_SECONDS))
    except TimeoutError as exc:
        raise RegexTimeoutError(
            "Pattern is taking too long (possible catastrophic backtracking) — "
            "try a simpler pattern.",
            detail=str(exc),
        ) from exc

    matches = [
        MatchDetail(
            index=i,
            text=m.group(0),
            start=m.start(),
            end=m.end(),
            groups=m.groups(),
        )
        for i, m in enumerate(found)
    ]
    return RegexResult(matches=matches, group_count=compiled.groups)
