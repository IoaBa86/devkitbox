"""Pure number base conversion logic — no Qt imports, fully unit-testable."""

from __future__ import annotations

from app.core.exceptions import ValidationError

BASES: dict[str, int] = {
    "Binary": 2,
    "Octal": 8,
    "Decimal": 10,
    "Hexadecimal": 16,
}

_PREFIXES: dict[int, str] = {2: "0b", 8: "0o", 16: "0x"}


def parse_value(text: str, base: int) -> int:
    stripped = text.strip()
    if not stripped:
        raise ValidationError("Enter a value")
    prefix = _PREFIXES.get(base, "")
    if prefix and stripped.lower().startswith(prefix):
        stripped = stripped[len(prefix) :]
    try:
        return int(stripped, base)
    except ValueError as exc:
        raise ValidationError(f"Invalid base-{base} value: {text!r}") from exc


def format_value(value: int, base: int, uppercase: bool = False) -> str:
    if base == 10:
        return str(value)
    if base == 2:
        text = bin(value)[2:] if value >= 0 else "-" + bin(value)[3:]
    elif base == 8:
        text = oct(value)[2:] if value >= 0 else "-" + oct(value)[3:]
    elif base == 16:
        text = hex(value)[2:] if value >= 0 else "-" + hex(value)[3:]
    else:
        raise ValidationError(f"Unsupported base: {base}")
    return text.upper() if uppercase else text


def convert_all(text: str, from_base: int) -> dict[str, str]:
    value = parse_value(text, from_base)
    return {name: format_value(value, base) for name, base in BASES.items()}


def bit_representation(value: int, bit_width: int = 32) -> str:
    if value < 0:
        value += 1 << bit_width
    return format(value & ((1 << bit_width) - 1), f"0{bit_width}b")
