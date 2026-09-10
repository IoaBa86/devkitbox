from __future__ import annotations

import pytest

from app.core.exceptions import ValidationError
from app.tools.timestamp.logic import from_iso, from_unix_millis, from_unix_seconds, now


def test_from_unix_seconds_known_value():
    result = from_unix_seconds(0)
    assert result.unix_seconds == 0
    assert result.utc == "1970-01-01 00:00:00 UTC"


def test_from_unix_millis_matches_seconds():
    result = from_unix_millis(1704110400000)
    assert result.unix_seconds == 1704110400
    assert result.unix_millis == 1704110400000


def test_from_iso_with_z_suffix():
    result = from_iso("2024-01-01T12:00:00Z")
    assert result.unix_seconds == 1704110400


def test_from_iso_with_offset():
    result = from_iso("2024-01-01T14:00:00+02:00")
    assert result.unix_seconds == 1704110400


def test_now_returns_current_epoch_roughly():
    import time

    result = now()
    assert abs(result.unix_seconds - int(time.time())) < 5


def test_invalid_unix_seconds_raises():
    with pytest.raises(ValidationError):
        from_unix_seconds(float("inf"))


def test_invalid_iso_raises():
    with pytest.raises(ValidationError):
        from_iso("not a date")
