"""Pure color conversion/contrast logic — no Qt imports, fully unit-testable."""

from __future__ import annotations

import colorsys
import re
from dataclasses import dataclass

from app.core.exceptions import ValidationError

_HEX_RE = re.compile(r"^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


@dataclass(frozen=True, slots=True)
class RGB:
    r: int
    g: int
    b: int


def parse_hex(value: str) -> RGB:
    match = _HEX_RE.match(value.strip())
    if not match:
        raise ValidationError(f"Invalid hex color: {value!r}")
    hex_digits = match.group(1)
    if len(hex_digits) == 3:
        hex_digits = "".join(c * 2 for c in hex_digits)
    r, g, b = (int(hex_digits[i : i + 2], 16) for i in (0, 2, 4))
    return RGB(r, g, b)


def rgb_to_hex(rgb: RGB, uppercase: bool = False) -> str:
    text = f"#{rgb.r:02x}{rgb.g:02x}{rgb.b:02x}"
    return text.upper() if uppercase else text


def rgb_to_hsl(rgb: RGB) -> tuple[float, float, float]:
    h, lightness, s = colorsys.rgb_to_hls(rgb.r / 255, rgb.g / 255, rgb.b / 255)
    return round(h * 360, 1), round(s * 100, 1), round(lightness * 100, 1)


def hsl_to_rgb(h: float, s: float, lightness: float) -> RGB:
    r, g, b = colorsys.hls_to_rgb(h / 360, lightness / 100, s / 100)
    return RGB(round(r * 255), round(g * 255), round(b * 255))


def rgb_to_hsv(rgb: RGB) -> tuple[float, float, float]:
    h, s, v = colorsys.rgb_to_hsv(rgb.r / 255, rgb.g / 255, rgb.b / 255)
    return round(h * 360, 1), round(s * 100, 1), round(v * 100, 1)


def format_rgb(rgb: RGB) -> str:
    return f"rgb({rgb.r}, {rgb.g}, {rgb.b})"


def format_hsl(h: float, s: float, lightness: float) -> str:
    return f"hsl({h}, {s}%, {lightness}%)"


def format_hsv(h: float, s: float, v: float) -> str:
    return f"hsv({h}, {s}%, {v}%)"


def _relative_luminance_channel(value: int) -> float:
    c = value / 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb: RGB) -> float:
    r, g, b = (_relative_luminance_channel(v) for v in (rgb.r, rgb.g, rgb.b))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(a: RGB, b: RGB) -> float:
    l1, l2 = relative_luminance(a), relative_luminance(b)
    lighter, darker = max(l1, l2), min(l1, l2)
    return round((lighter + 0.05) / (darker + 0.05), 2)


def wcag_level(ratio: float, large_text: bool = False) -> str:
    aa_threshold = 3.0 if large_text else 4.5
    aaa_threshold = 4.5 if large_text else 7.0
    if ratio >= aaa_threshold:
        return "AAA"
    if ratio >= aa_threshold:
        return "AA"
    return "Fail"


WHITE = RGB(255, 255, 255)
BLACK = RGB(0, 0, 0)
