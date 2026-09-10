"""Pure whitespace-cleanup logic — no Qt imports, fully unit-testable."""

from __future__ import annotations

import re

_TRAILING_WS_RE = re.compile(r"[ \t]+$", re.MULTILINE)
_MULTI_SPACE_RE = re.compile(r"[ \t]{2,}")
_MULTI_BLANK_LINE_RE = re.compile(r"\n{3,}")


def normalize_line_endings(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def trim_trailing_whitespace(text: str) -> str:
    return _TRAILING_WS_RE.sub("", text)


def trim_leading_trailing(text: str) -> str:
    return "\n".join(line.strip() for line in text.splitlines())


def collapse_spaces(text: str) -> str:
    return "\n".join(_MULTI_SPACE_RE.sub(" ", line) for line in text.splitlines())


def collapse_blank_lines(text: str) -> str:
    return _MULTI_BLANK_LINE_RE.sub("\n\n", text)


def remove_blank_lines(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if line.strip())


def tabs_to_spaces(text: str, tab_size: int = 4) -> str:
    return text.expandtabs(tab_size)


def spaces_to_tabs(text: str, tab_size: int = 4) -> str:
    indent_re = re.compile(rf"^( {{{tab_size}}})+")

    def replace_indent(line: str) -> str:
        match = indent_re.match(line)
        if not match:
            return line
        spaces = match.group(0)
        tabs = "\t" * (len(spaces) // tab_size)
        return tabs + line[len(spaces) :]

    return "\n".join(replace_indent(line) for line in text.splitlines())


def ensure_trailing_newline(text: str) -> str:
    if not text:
        return text
    return text if text.endswith("\n") else text + "\n"


def clean_all(text: str, tab_size: int = 4) -> str:
    text = normalize_line_endings(text)
    text = trim_trailing_whitespace(text)
    text = collapse_blank_lines(text)
    text = tabs_to_spaces(text, tab_size)
    return ensure_trailing_newline(text)
