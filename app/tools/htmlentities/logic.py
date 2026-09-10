"""Pure HTML entity encode/decode logic — no Qt imports, fully unit-testable."""

from __future__ import annotations

import html


def encode_entities(text: str, escape_quotes: bool = True) -> str:
    return html.escape(text, quote=escape_quotes)


def decode_entities(text: str) -> str:
    return html.unescape(text)
