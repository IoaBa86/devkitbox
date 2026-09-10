"""Pure Markdown-analysis logic — no Qt imports, fully unit-testable.

Rendering itself is done by Qt's native ``QTextBrowser.setMarkdown`` in the
widget; this module only extracts structural info (headings, word count).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)
_WORD_RE = re.compile(r"\S+")


@dataclass(frozen=True, slots=True)
class Heading:
    level: int
    title: str
    slug: str


def _slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9\s-]", "", title.lower())
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug


def extract_headings(text: str) -> list[Heading]:
    headings: list[Heading] = []
    for match in _HEADING_RE.finditer(text):
        level = len(match.group(1))
        title = match.group(2).strip()
        headings.append(Heading(level=level, title=title, slug=_slugify(title)))
    return headings


def build_toc(headings: list[Heading]) -> str:
    lines = []
    for heading in headings:
        indent = "  " * (heading.level - 1)
        lines.append(f"{indent}- [{heading.title}](#{heading.slug})")
    return "\n".join(lines)


def word_count(text: str) -> int:
    return len(_WORD_RE.findall(text))
