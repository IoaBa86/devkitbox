from __future__ import annotations

from datetime import datetime

import pytest

from app.core.exceptions import ValidationError
from app.tools.timezone.logic import convert_to_zones


def test_convert_to_zones_utc_to_new_york():
    source = datetime(2026, 1, 1, 12, 0, 0)
    results = convert_to_zones(source, "UTC", ["America/New_York"])
    assert len(results) == 1
    result = results[0]
    assert result.zone_name == "America/New_York"
    # New York is UTC-5 in January (standard time).
    assert result.local_time.hour == 7
    assert result.utc_offset == "-05:00"


def test_convert_to_zones_utc_offset_zero_for_utc():
    source = datetime(2026, 6, 1, 12, 0, 0)
    results = convert_to_zones(source, "UTC", ["UTC"])
    assert results[0].utc_offset == "+00:00"


def test_convert_to_zones_handles_dst():
    # New York is UTC-4 in July (daylight saving time).
    source = datetime(2026, 7, 1, 12, 0, 0)
    results = convert_to_zones(source, "UTC", ["America/New_York"])
    assert results[0].utc_offset == "-04:00"


def test_convert_to_zones_positive_offset():
    source = datetime(2026, 1, 1, 0, 0, 0)
    results = convert_to_zones(source, "UTC", ["Asia/Tokyo"])
    assert results[0].utc_offset == "+09:00"
    assert results[0].local_time.hour == 9


def test_convert_to_zones_multiple_targets():
    source = datetime(2026, 1, 1, 12, 0, 0)
    results = convert_to_zones(source, "UTC", ["America/New_York", "Asia/Tokyo", "UTC"])
    assert [r.zone_name for r in results] == ["America/New_York", "Asia/Tokyo", "UTC"]


def test_convert_to_zones_non_utc_source():
    # Noon in Tokyo should be 03:00 UTC the same day.
    source = datetime(2026, 1, 1, 12, 0, 0)
    results = convert_to_zones(source, "Asia/Tokyo", ["UTC"])
    assert results[0].local_time.hour == 3


def test_convert_to_zones_unknown_source_zone_raises():
    with pytest.raises(ValidationError):
        convert_to_zones(datetime(2026, 1, 1), "Not/AZone", ["UTC"])


def test_convert_to_zones_unknown_target_zone_raises():
    with pytest.raises(ValidationError):
        convert_to_zones(datetime(2026, 1, 1), "UTC", ["Not/AZone"])
