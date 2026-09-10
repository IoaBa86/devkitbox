"""Pure unit conversion logic (data size, time duration) — no Qt imports."""

from __future__ import annotations

from app.core.exceptions import ValidationError

DATA_SIZE_UNITS: dict[str, float] = {
    "B": 1,
    "KB": 1000,
    "MB": 1000**2,
    "GB": 1000**3,
    "TB": 1000**4,
    "PB": 1000**5,
    "KiB": 1024,
    "MiB": 1024**2,
    "GiB": 1024**3,
    "TiB": 1024**4,
    "PiB": 1024**5,
}

TIME_UNITS: dict[str, float] = {
    "Milliseconds": 0.001,
    "Seconds": 1,
    "Minutes": 60,
    "Hours": 3600,
    "Days": 86400,
    "Weeks": 604800,
}

UNIT_FAMILIES: dict[str, dict[str, float]] = {
    "Data Size": DATA_SIZE_UNITS,
    "Time Duration": TIME_UNITS,
}


def convert(value: float, from_unit: str, to_unit: str, family: str) -> float:
    units = UNIT_FAMILIES.get(family)
    if units is None:
        raise ValidationError(f"Unknown unit family: {family}")
    if from_unit not in units:
        raise ValidationError(f"Unknown unit: {from_unit}")
    if to_unit not in units:
        raise ValidationError(f"Unknown unit: {to_unit}")

    base_value = value * units[from_unit]
    return base_value / units[to_unit]


def convert_to_all(value: float, from_unit: str, family: str) -> dict[str, float]:
    units = UNIT_FAMILIES.get(family)
    if units is None:
        raise ValidationError(f"Unknown unit family: {family}")
    if from_unit not in units:
        raise ValidationError(f"Unknown unit: {from_unit}")

    return {unit: convert(value, from_unit, unit, family) for unit in units}
