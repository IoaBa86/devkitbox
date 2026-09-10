from __future__ import annotations

from datetime import datetime

import pytest

from app.core.exceptions import ValidationError
from app.tools.cron.logic import describe, next_run_times, parse_cron


def test_parse_cron_wrong_field_count_raises():
    with pytest.raises(ValidationError):
        parse_cron("* * *")


def test_parse_cron_wildcard_expands_full_range():
    schedule = parse_cron("* * * * *")
    assert schedule.minute == frozenset(range(0, 60))
    assert schedule.hour == frozenset(range(0, 24))
    assert schedule.dom_restricted is False
    assert schedule.dow_restricted is False


def test_parse_cron_step_value():
    schedule = parse_cron("*/15 * * * *")
    assert schedule.minute == frozenset({0, 15, 30, 45})


def test_parse_cron_range():
    schedule = parse_cron("0 9-17 * * *")
    assert schedule.hour == frozenset(range(9, 18))


def test_parse_cron_list():
    schedule = parse_cron("0 0 * * 1,3,5")
    assert schedule.day_of_week == frozenset({1, 3, 5})


def test_parse_cron_sunday_7_normalizes_to_0():
    schedule = parse_cron("0 0 * * 7")
    assert schedule.day_of_week == frozenset({0})


def test_parse_cron_out_of_range_raises():
    with pytest.raises(ValidationError):
        parse_cron("60 * * * *")


def test_parse_cron_invalid_literal_raises():
    with pytest.raises(ValidationError):
        parse_cron("abc * * * *")


def test_next_run_times_every_minute():
    schedule = parse_cron("* * * * *")
    after = datetime(2026, 1, 1, 12, 0)
    runs = next_run_times(schedule, after, count=3)
    assert runs == [
        datetime(2026, 1, 1, 12, 1),
        datetime(2026, 1, 1, 12, 2),
        datetime(2026, 1, 1, 12, 3),
    ]


def test_next_run_times_daily_at_specific_time():
    schedule = parse_cron("30 9 * * *")
    after = datetime(2026, 1, 1, 10, 0)  # already past 09:30 today
    runs = next_run_times(schedule, after, count=1)
    assert runs == [datetime(2026, 1, 2, 9, 30)]


def test_next_run_times_weekday_only():
    schedule = parse_cron("0 9 * * 1-5")
    # 2026-01-03 is a Saturday
    after = datetime(2026, 1, 3, 0, 0)
    runs = next_run_times(schedule, after, count=1)
    assert runs[0].weekday() < 5  # Monday-Friday
    assert runs[0] == datetime(2026, 1, 5, 9, 0)  # next Monday


def test_next_run_times_dom_or_dow_semantics():
    # "on the 1st OR on a Monday" — vixie-cron OR quirk when both restricted
    schedule = parse_cron("0 0 1 * 1")
    after = datetime(2026, 1, 4, 0, 0)  # Sunday, before both 2026-01-05 (Mon) and 2026-02-01
    runs = next_run_times(schedule, after, count=2)
    assert runs[0] == datetime(2026, 1, 5, 0, 0)  # next Monday
    assert runs[1] == datetime(2026, 1, 12, 0, 0)  # Monday after that


def test_describe_every_minute():
    schedule = parse_cron("* * * * *")
    assert describe(schedule) == "Every minute"


def test_describe_specific_time():
    schedule = parse_cron("30 9 * * *")
    assert describe(schedule) == "At 09:30"


def test_describe_weekdays():
    schedule = parse_cron("0 9 * * 1-5")
    result = describe(schedule)
    assert "At 09:00" in result
    assert "Monday" in result and "Friday" in result
