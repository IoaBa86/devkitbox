"""Pure URL encode/decode and query-string logic — no Qt imports, fully unit-testable."""

from __future__ import annotations

from urllib.parse import parse_qsl, quote, unquote, urlencode

_URL_SAFE_CHARS = "/:?#[]@!$&'()*+,;=~"


def encode_url(text: str) -> str:
    """Encodes a full URL, preserving structural characters like / and ?."""
    return quote(text, safe=_URL_SAFE_CHARS)


def encode_component(text: str) -> str:
    """Encodes a single component (e.g. a query value) — every reserved char is escaped."""
    return quote(text, safe="")


def decode_url(text: str) -> str:
    return unquote(text)


def parse_query_string(query: str) -> list[tuple[str, str]]:
    cleaned = query.split("?", 1)[-1]
    return parse_qsl(cleaned, keep_blank_values=True)


def build_query_string(pairs: list[tuple[str, str]]) -> str:
    return urlencode(pairs)


def parse_lines_to_pairs(text: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        key, _, value = line.partition("=")
        pairs.append((key.strip(), value.strip()))
    return pairs
