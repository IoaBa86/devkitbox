"""Pure timezone conversion logic — no Qt imports, fully unit-testable.

Uses stdlib ``zoneinfo``. Windows has no system IANA tz database, so this
app depends on the ``tzdata`` package (pure-Python, CPython-maintained)
to make zoneinfo work at all — without it every lookup below raises.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.core.exceptions import ValidationError

COMMON_ZONES: tuple[str, ...] = (
    "UTC",
    "America/New_York",
    "America/Chicago",
    "America/Denver",
    "America/Los_Angeles",
    "America/Sao_Paulo",
    "Europe/London",
    "Europe/Paris",
    "Europe/Berlin",
    "Europe/Moscow",
    "Africa/Cairo",
    "Asia/Dubai",
    "Asia/Kolkata",
    "Asia/Shanghai",
    "Asia/Tokyo",
    "Asia/Singapore",
    "Australia/Sydney",
    "Pacific/Auckland",
)


@dataclass(frozen=True, slots=True)
class ZoneResult:
    zone_name: str
    local_time: datetime
    utc_offset: str
    abbreviation: str | None


def _load_zone(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError as exc:
        raise ValidationError(f"Unknown timezone: {name!r}") from exc


def convert_to_zones(
    source_time: datetime, source_zone: str, target_zones: list[str]
) -> list[ZoneResult]:
    if source_time.tzinfo is None:
        source_time = source_time.replace(tzinfo=_load_zone(source_zone))
    else:
        source_time = source_time.astimezone(_load_zone(source_zone))

    results = []
    for zone_name in target_zones:
        zone = _load_zone(zone_name)
        local_time = source_time.astimezone(zone)
        offset = local_time.utcoffset()
        offset_str = _format_offset(offset)
        results.append(
            ZoneResult(
                zone_name=zone_name,
                local_time=local_time,
                utc_offset=offset_str,
                abbreviation=local_time.tzname(),
            )
        )
    return results


def _format_offset(offset) -> str:
    if offset is None:
        return "+00:00"
    total_minutes = int(offset.total_seconds() // 60)
    sign = "+" if total_minutes >= 0 else "-"
    total_minutes = abs(total_minutes)
    hours, minutes = divmod(total_minutes, 60)
    return f"{sign}{hours:02d}:{minutes:02d}"
