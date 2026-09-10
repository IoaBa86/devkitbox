from __future__ import annotations

import pytest

from app.core.exceptions import ValidationError
from app.tools.qrcode.logic import generate_matrix


def test_generate_matrix_basic():
    matrix = generate_matrix("hello")
    assert len(matrix) > 0
    assert all(len(row) == len(matrix) for row in matrix)
    assert all(isinstance(cell, bool) for row in matrix for cell in row)


def test_generate_matrix_empty_raises():
    with pytest.raises(ValidationError):
        generate_matrix("")


def test_generate_matrix_too_long_raises():
    with pytest.raises(ValidationError):
        generate_matrix("x" * 3000)


def test_generate_matrix_unknown_error_correction_raises():
    with pytest.raises(ValidationError):
        generate_matrix("hello", "Ultra (99%)")


def test_generate_matrix_higher_error_correction_grows_matrix_for_same_data():
    low = generate_matrix("a" * 100, "Low (7%)")
    high = generate_matrix("a" * 100, "High (30%)")
    assert len(high) >= len(low)


def test_generate_matrix_deterministic():
    a = generate_matrix("same input")
    b = generate_matrix("same input")
    assert a == b


def test_generate_matrix_too_long_for_high_error_correction_raises_cleanly():
    # Regression: qrcode's High (30%) capacity ceiling (~1273 chars) is far
    # below _MAX_DATA_LENGTH (2953, the Low-EC ceiling), so data in that gap
    # must still raise ValidationError — not an unhandled ValueError from
    # the qrcode library's version bisection.
    with pytest.raises(ValidationError):
        generate_matrix("x" * 2900, "High (30%)")
