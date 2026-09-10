"""Pure timestamp conversion logic — no Qt imports, fully unit-testable."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from app.core.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class TimestampResult:
    unix_seconds: int
    unix_millis: int
    utc: str
    local: str
    iso8601: str


def _from_datetime(dt: datetime) -> TimestampResult:
    if dt.tzinfo is None:
        dt = dt.astimezone()
    dt_utc = dt.astimezone(UTC)
    dt_local = dt.astimezone()
    return TimestampResult(
        unix_seconds=int(dt_utc.timestamp()),
        unix_millis=int(dt_utc.timestamp() * 1000),
        utc=dt_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
        local=dt_local.strftime("%Y-%m-%d %H:%M:%S %z"),
        iso8601=dt_utc.isoformat(),
    )


def now() -> TimestampResult:
    return _from_datetime(datetime.now(UTC))


def from_unix_seconds(value: float) -> TimestampResult:
    try:
        dt = datetime.fromtimestamp(float(value), tz=UTC)
    except (ValueError, OverflowError, OSError) as exc:
        raise ValidationError("Invalid Unix timestamp (seconds)", detail=str(exc)) from exc
    return _from_datetime(dt)


def from_unix_millis(value: float) -> TimestampResult:
    try:
        dt = datetime.fromtimestamp(float(value) / 1000, tz=UTC)
    except (ValueError, OverflowError, OSError) as exc:
        raise ValidationError("Invalid Unix timestamp (milliseconds)", detail=str(exc)) from exc
    return _from_datetime(dt)


def from_iso(text: str) -> TimestampResult:
    normalized = text.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValidationError(
            "Invalid date/time",
            detail="Expected ISO 8601, e.g. 2024-01-01T12:00:00Z",
        ) from exc
    return _from_datetime(dt)
