"""Pure 5-field cron expression parsing/explanation logic — no Qt imports.

Standard vixie-cron fields: minute hour day-of-month month day-of-week.
When both day-of-month and day-of-week are restricted (not ``*``), a day
matches if *either* field matches (the traditional cron OR quirk) — not
both, which is the mistake most from-scratch cron parsers make.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from app.core.exceptions import ValidationError

_FIELD_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day_of_month": (1, 31),
    "month": (1, 12),
    "day_of_week": (0, 7),  # 0 and 7 both mean Sunday
}
_FIELD_NAMES = list(_FIELD_RANGES.keys())

_MONTH_NAMES = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]
_WEEKDAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

_MAX_ITERATIONS = 4 * 366 * 24 * 60  # ~4 years of minutes


@dataclass(frozen=True, slots=True)
class CronSchedule:
    minute: frozenset[int]
    hour: frozenset[int]
    day_of_month: frozenset[int]
    month: frozenset[int]
    day_of_week: frozenset[int]
    dom_restricted: bool
    dow_restricted: bool


def _expand_field(field_text: str, name: str) -> frozenset[int]:
    low, high = _FIELD_RANGES[name]
    values: set[int] = set()

    for part in field_text.split(","):
        part = part.strip()
        if not part:
            raise ValidationError(f"Empty value in {name} field")

        step = 1
        if "/" in part:
            base, step_text = part.split("/", 1)
            try:
                step = int(step_text)
            except ValueError as exc:
                raise ValidationError(f"Invalid step in {name} field: {part!r}") from exc
            if step <= 0:
                raise ValidationError(f"Step must be positive in {name} field: {part!r}")
        else:
            base = part

        if base == "*":
            start, end = low, high
        elif "-" in base:
            start_text, end_text = base.split("-", 1)
            try:
                start, end = int(start_text), int(end_text)
            except ValueError as exc:
                raise ValidationError(f"Invalid range in {name} field: {part!r}") from exc
        else:
            try:
                start = end = int(base)
            except ValueError as exc:
                raise ValidationError(f"Invalid value in {name} field: {part!r}") from exc

        if not (low <= start <= high) or not (low <= end <= high) or start > end:
            raise ValidationError(f"Value out of range in {name} field: {part!r} ({low}-{high})")

        values.update(range(start, end + 1, step))

    return frozenset(v % 7 if name == "day_of_week" and v == 7 else v for v in values)


def parse_cron(expression: str) -> CronSchedule:
    fields = expression.strip().split()
    if len(fields) != 5:
        raise ValidationError(
            f"Expected 5 fields (minute hour day-of-month month day-of-week), got {len(fields)}"
        )

    minute, hour, dom, month, dow = (
        _expand_field(text, name) for text, name in zip(fields, _FIELD_NAMES, strict=True)
    )

    return CronSchedule(
        minute=minute,
        hour=hour,
        day_of_month=dom,
        month=month,
        day_of_week=dow,
        dom_restricted=fields[2].strip() != "*",
        dow_restricted=fields[4].strip() != "*",
    )


def _day_matches(schedule: CronSchedule, dt: datetime) -> bool:
    dom_match = dt.day in schedule.day_of_month
    dow_match = (dt.isoweekday() % 7) in schedule.day_of_week

    if schedule.dom_restricted and schedule.dow_restricted:
        return dom_match or dow_match
    return dom_match and dow_match


def next_run_times(schedule: CronSchedule, after: datetime, count: int = 5) -> list[datetime]:
    results: list[datetime] = []
    candidate = (after + timedelta(minutes=1)).replace(second=0, microsecond=0)

    for _ in range(_MAX_ITERATIONS):
        if len(results) >= count:
            break
        if (
            candidate.month in schedule.month
            and _day_matches(schedule, candidate)
            and candidate.hour in schedule.hour
            and candidate.minute in schedule.minute
        ):
            results.append(candidate)
        candidate += timedelta(minutes=1)

    return results


def _field_phrase(values: frozenset[int], low: int, high: int, unit: str) -> str | None:
    """Return None for "every <unit>" (no restriction worth mentioning)."""
    if len(values) == high - low + 1:
        return None
    sorted_values = sorted(values)
    if len(sorted_values) == 1:
        return f"{unit} {sorted_values[0]}"
    return f"{unit} {', '.join(str(v) for v in sorted_values)}"


def describe(schedule: CronSchedule) -> str:
    minute_phrase = _field_phrase(schedule.minute, 0, 59, "minute")
    hour_phrase = _field_phrase(schedule.hour, 0, 23, "hour")

    if minute_phrase is None and hour_phrase is None:
        time_part = "Every minute"
    elif len(schedule.minute) == 1 and len(schedule.hour) == 1:
        m, h = next(iter(schedule.minute)), next(iter(schedule.hour))
        time_part = f"At {h:02d}:{m:02d}"
    elif hour_phrase is None:
        time_part = f"At {minute_phrase.replace('minute', 'minute(s)', 1)} past every hour"
    elif minute_phrase is None:
        time_part = f"Every minute during {hour_phrase.replace('hour', 'hour(s)', 1)}"
    else:
        time_part = f"At {minute_phrase} of {hour_phrase.replace('hour', 'hour(s)', 1)}"

    clauses = [time_part]

    if schedule.month and len(schedule.month) != 12:
        months = ", ".join(_MONTH_NAMES[m - 1] for m in sorted(schedule.month))
        clauses.append(f"in {months}")

    if schedule.dom_restricted and schedule.dow_restricted:
        days = ", ".join(str(d) for d in sorted(schedule.day_of_month))
        weekdays = ", ".join(_WEEKDAY_NAMES[d] for d in sorted(schedule.day_of_week))
        clauses.append(f"on day {days} of the month or on {weekdays}")
    elif schedule.dom_restricted:
        days = ", ".join(str(d) for d in sorted(schedule.day_of_month))
        clauses.append(f"on day {days} of the month")
    elif schedule.dow_restricted:
        weekdays = ", ".join(_WEEKDAY_NAMES[d] for d in sorted(schedule.day_of_week))
        clauses.append(f"on {weekdays}")

    return ", ".join(clauses)
