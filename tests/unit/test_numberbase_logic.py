from __future__ import annotations

import pytest

from app.core.exceptions import ValidationError
from app.tools.numberbase.logic import bit_representation, convert_all, format_value, parse_value


def test_parse_value_decimal():
    assert parse_value("42", 10) == 42


def test_parse_value_hex_with_prefix():
    assert parse_value("0x2A", 16) == 42


def test_parse_value_hex_without_prefix():
    assert parse_value("2A", 16) == 42


def test_parse_value_binary_with_prefix():
    assert parse_value("0b101010", 2) == 42


def test_parse_value_empty_raises():
    with pytest.raises(ValidationError):
        parse_value("", 10)


def test_parse_value_invalid_digits_raises():
    with pytest.raises(ValidationError):
        parse_value("xyz", 10)


def test_format_value_binary():
    assert format_value(42, 2) == "101010"


def test_format_value_hex_lowercase_default():
    assert format_value(255, 16) == "ff"


def test_format_value_hex_uppercase():
    assert format_value(255, 16, uppercase=True) == "FF"


def test_format_value_negative():
    assert format_value(-42, 2) == "-101010"


def test_convert_all_round_trip():
    result = convert_all("42", 10)
    assert result == {
        "Binary": "101010",
        "Octal": "52",
        "Decimal": "42",
        "Hexadecimal": "2a",
    }


def test_bit_representation_positive():
    assert bit_representation(5, bit_width=8) == "00000101"


def test_bit_representation_negative_twos_complement():
    assert bit_representation(-1, bit_width=8) == "11111111"
