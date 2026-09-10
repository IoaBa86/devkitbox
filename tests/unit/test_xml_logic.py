from __future__ import annotations

import pytest

from app.core.exceptions import ValidationError
from app.tools.xml.logic import format_xml, minify_xml, validate_xml


def test_validate_xml_valid():
    validate_xml("<root><child>value</child></root>")  # must not raise


def test_validate_xml_invalid_raises():
    with pytest.raises(ValidationError):
        validate_xml("<root><child></root>")


def test_validate_xml_empty_raises():
    with pytest.raises(ValidationError):
        validate_xml("")


def test_format_xml_pretty_prints():
    result = format_xml("<root><child>value</child></root>")
    assert "<root>" in result
    assert "  <child>value</child>" in result


def test_format_xml_invalid_raises():
    with pytest.raises(ValidationError):
        format_xml("<root><child></root>")


def test_minify_xml_removes_whitespace():
    result = minify_xml("<root>\n  <child>value</child>\n</root>")
    assert result == "<root><child>value</child></root>"


def test_minify_xml_invalid_raises():
    with pytest.raises(ValidationError):
        minify_xml("not xml at all <")


def test_validate_xml_rejects_billion_laughs_entity_expansion():
    # Python's stdlib pyexpat has a built-in amplification-factor guard
    # (CPython bpo-44394) — this must raise cleanly, not hang or OOM.
    entities = ['<!ENTITY lol "lol">']
    for i in range(1, 9):
        prev = "lol" if i == 1 else f"lol{i - 1}"
        entities.append(f'<!ENTITY lol{i} "' + ("&" + prev + ";") * 10 + '">')
    dtd = "\n ".join(entities)
    bomb = f"""<?xml version="1.0"?>
<!DOCTYPE lolz [
 {dtd}
 <!ELEMENT lolz (#PCDATA)>
]>
<lolz>&lol8;</lolz>"""

    with pytest.raises(ValidationError):
        validate_xml(bomb)
