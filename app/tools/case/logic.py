"""Pure text-case conversion logic — no Qt imports, fully unit-testable."""

from __future__ import annotations

import re

_WORD_SPLIT_RE = re.compile(r"[^a-zA-Z0-9]+|(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")


def split_words(text: str) -> list[str]:
    return [w for w in _WORD_SPLIT_RE.split(text.strip()) if w]


def to_lower(text: str) -> str:
    return text.lower()


def to_upper(text: str) -> str:
    return text.upper()


def to_title(text: str) -> str:
    return " ".join(w.capitalize() for w in split_words(text))


def to_sentence(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return ""
    return stripped[0].upper() + stripped[1:].lower()


def to_camel(text: str) -> str:
    words = split_words(text)
    if not words:
        return ""
    return words[0].lower() + "".join(w.capitalize() for w in words[1:])


def to_pascal(text: str) -> str:
    return "".join(w.capitalize() for w in split_words(text))


def to_snake(text: str) -> str:
    return "_".join(w.lower() for w in split_words(text))


def to_kebab(text: str) -> str:
    return "-".join(w.lower() for w in split_words(text))


def to_constant(text: str) -> str:
    return "_".join(w.upper() for w in split_words(text))


CASE_CONVERTERS: dict[str, callable] = {
    "lowercase": to_lower,
    "UPPERCASE": to_upper,
    "Title Case": to_title,
    "Sentence case": to_sentence,
    "camelCase": to_camel,
    "PascalCase": to_pascal,
    "snake_case": to_snake,
    "kebab-case": to_kebab,
    "CONSTANT_CASE": to_constant,
}
