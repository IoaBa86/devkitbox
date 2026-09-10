from __future__ import annotations

import uuid

import pytest

from app.tools.uuid.logic import (
    NAMESPACE_PRESETS,
    format_uuid,
    generate_bulk,
    generate_v4,
    generate_v5,
)


def test_generate_v4_is_valid_uuid4():
    value = generate_v4()
    assert isinstance(value, uuid.UUID)
    assert value.version == 4


def test_generate_v5_is_deterministic():
    a = generate_v5(NAMESPACE_PRESETS["DNS"], "example.com")
    b = generate_v5(NAMESPACE_PRESETS["DNS"], "example.com")
    assert a == b
    assert a.version == 5


def test_generate_bulk_v4_returns_unique_values():
    values = generate_bulk(4, 50)
    assert len(values) == 50
    assert len(set(values)) == 50


def test_generate_bulk_invalid_version_raises():
    with pytest.raises(ValueError):
        generate_bulk(3, 1)


def test_format_uuid_uppercase_braces_no_hyphens():
    value = uuid.UUID("12345678-1234-5678-1234-567812345678")
    result = format_uuid(value, uppercase=True, braces=True, hyphens=False)
    assert result == "{12345678123456781234567812345678}".upper()


def test_format_uuid_default_matches_str():
    value = uuid.uuid4()
    assert format_uuid(value) == str(value)
