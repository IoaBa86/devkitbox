"""Pure XML formatting/validation logic — no Qt imports, fully unit-testable."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from xml.dom import minidom
from xml.parsers.expat import ExpatError

from app.core.exceptions import ValidationError


def validate_xml(text: str) -> None:
    try:
        ET.fromstring(text)
    except ET.ParseError as exc:
        line, column = exc.position
        raise ValidationError(f"Invalid XML: {exc.msg}", line=line, column=column) from exc


def format_xml(text: str, indent: str = "  ") -> str:
    validate_xml(text)
    try:
        parsed = minidom.parseString(text)
    except ExpatError as exc:
        raise ValidationError(f"Invalid XML: {exc}") from exc

    pretty = parsed.toprettyxml(indent=indent)
    lines = [line for line in pretty.splitlines() if line.strip()]
    return "\n".join(lines)


def _strip_whitespace(element: ET.Element) -> None:
    if element.text is not None and not element.text.strip():
        element.text = None
    if element.tail is not None and not element.tail.strip():
        element.tail = None
    for child in element:
        _strip_whitespace(child)


def minify_xml(text: str) -> str:
    validate_xml(text)
    root = ET.fromstring(text)
    _strip_whitespace(root)
    return ET.tostring(root, encoding="unicode")
