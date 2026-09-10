from __future__ import annotations

from app.tools.htmlentities.logic import decode_entities, encode_entities


def test_encode_entities_basic():
    assert encode_entities("Tom & Jerry") == "Tom &amp; Jerry"


def test_encode_entities_tags():
    assert encode_entities("<div>") == "&lt;div&gt;"


def test_encode_entities_quotes_default_on():
    assert encode_entities('say "hi"') == "say &quot;hi&quot;"


def test_encode_entities_quotes_off():
    assert encode_entities('say "hi"', escape_quotes=False) == 'say "hi"'


def test_decode_entities_named():
    assert decode_entities("Tom &amp; Jerry") == "Tom & Jerry"


def test_decode_entities_numeric():
    assert decode_entities("&#65;&#66;&#67;") == "ABC"


def test_decode_entities_hex_numeric():
    assert decode_entities("&#x41;&#x42;") == "AB"


def test_encode_decode_round_trip():
    original = '<a href="x">Tom & Jerry</a>'
    assert decode_entities(encode_entities(original)) == original
