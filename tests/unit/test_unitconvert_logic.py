from __future__ import annotations

import pytest

from app.core.exceptions import ValidationError
from app.tools.unitconvert.logic import convert, convert_to_all


def test_convert_kb_to_bytes():
    assert convert(1, "KB", "B", "Data Size") == 1000


def test_convert_mib_to_kib():
    assert convert(1, "MiB", "KiB", "Data Size") == 1024


def test_convert_decimal_vs_binary_differ():
    assert convert(1, "GB", "B", "Data Size") != convert(1, "GiB", "B", "Data Size")


def test_convert_same_unit_is_identity():
    assert convert(42, "MB", "MB", "Data Size") == 42


def test_convert_hours_to_minutes():
    assert convert(2, "Hours", "Minutes", "Time Duration") == 120


def test_convert_days_to_seconds():
    assert convert(1, "Days", "Seconds", "Time Duration") == 86400


def test_convert_unknown_family_raises():
    with pytest.raises(ValidationError):
        convert(1, "B", "KB", "Weight")


def test_convert_unknown_unit_raises():
    with pytest.raises(ValidationError):
        convert(1, "Furlongs", "B", "Data Size")


def test_convert_to_all_includes_every_unit_in_family():
    result = convert_to_all(1024, "B", "Data Size")
    assert set(result.keys()) == {
        "B",
        "KB",
        "MB",
        "GB",
        "TB",
        "PB",
        "KiB",
        "MiB",
        "GiB",
        "TiB",
        "PiB",
    }
    assert result["KiB"] == 1.0


def test_convert_to_all_round_trip_to_source_unit():
    result = convert_to_all(5, "Minutes", "Time Duration")
    assert result["Minutes"] == 5
