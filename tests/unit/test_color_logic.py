from __future__ import annotations

import pytest

from app.core.exceptions import ValidationError
from app.tools.color.logic import (
    BLACK,
    RGB,
    WHITE,
    contrast_ratio,
    format_hsl,
    format_hsv,
    format_rgb,
    hsl_to_rgb,
    parse_hex,
    rgb_to_hex,
    rgb_to_hsl,
    rgb_to_hsv,
    wcag_level,
)


def test_parse_hex_six_digit():
    assert parse_hex("#7C5CFF") == RGB(124, 92, 255)


def test_parse_hex_three_digit_shorthand():
    assert parse_hex("#fff") == RGB(255, 255, 255)


def test_parse_hex_without_hash_prefix():
    assert parse_hex("000000") == RGB(0, 0, 0)


def test_parse_hex_invalid_raises():
    with pytest.raises(ValidationError):
        parse_hex("not-a-color")


def test_rgb_to_hex_roundtrip():
    rgb = RGB(124, 92, 255)
    assert rgb_to_hex(rgb) == "#7c5cff"
    assert rgb_to_hex(rgb, uppercase=True) == "#7C5CFF"


def test_rgb_to_hsl_white():
    assert rgb_to_hsl(RGB(255, 255, 255)) == (0.0, 0.0, 100.0)


def test_rgb_to_hsl_black():
    assert rgb_to_hsl(RGB(0, 0, 0)) == (0.0, 0.0, 0.0)


def test_hsl_to_rgb_roundtrip():
    original = RGB(124, 92, 255)
    h, s, lightness = rgb_to_hsl(original)
    result = hsl_to_rgb(h, s, lightness)
    assert abs(result.r - original.r) <= 1
    assert abs(result.g - original.g) <= 1
    assert abs(result.b - original.b) <= 1


def test_rgb_to_hsv_pure_red():
    assert rgb_to_hsv(RGB(255, 0, 0)) == (0.0, 100.0, 100.0)


def test_format_rgb():
    assert format_rgb(RGB(1, 2, 3)) == "rgb(1, 2, 3)"


def test_format_hsl():
    assert format_hsl(210.0, 50.0, 40.0) == "hsl(210.0, 50.0%, 40.0%)"


def test_format_hsv():
    assert format_hsv(210.0, 50.0, 40.0) == "hsv(210.0, 50.0%, 40.0%)"


def test_contrast_ratio_black_on_white_is_max():
    assert contrast_ratio(BLACK, WHITE) == 21.0


def test_contrast_ratio_same_color_is_one():
    assert contrast_ratio(RGB(100, 100, 100), RGB(100, 100, 100)) == 1.0


def test_contrast_ratio_symmetric():
    a, b = RGB(10, 20, 30), RGB(200, 210, 220)
    assert contrast_ratio(a, b) == contrast_ratio(b, a)


def test_wcag_level_aaa():
    assert wcag_level(8.0) == "AAA"


def test_wcag_level_aa():
    assert wcag_level(5.0) == "AA"


def test_wcag_level_fail():
    assert wcag_level(2.0) == "Fail"


def test_wcag_level_large_text_lower_thresholds():
    assert wcag_level(3.5, large_text=True) == "AA"
