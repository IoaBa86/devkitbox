from __future__ import annotations

import pytest

from app.tools.password.logic import (
    DIGITS,
    LOWERCASE,
    SYMBOLS,
    UPPERCASE,
    PasswordOptions,
    generate_passphrase,
    generate_password,
    password_entropy_bits,
    strength_label,
)


def test_generate_password_default_length():
    value = generate_password(PasswordOptions())
    assert len(value) == 16


def test_generate_password_length_respected():
    value = generate_password(PasswordOptions(length=32))
    assert len(value) == 32


def test_generate_password_contains_each_selected_set():
    options = PasswordOptions(length=40, lowercase=True, uppercase=True, digits=True, symbols=True)
    value = generate_password(options)
    assert any(c in LOWERCASE for c in value)
    assert any(c in UPPERCASE for c in value)
    assert any(c in DIGITS for c in value)
    assert any(c in SYMBOLS for c in value)


def test_generate_password_no_charset_raises():
    options = PasswordOptions(lowercase=False, uppercase=False, digits=False, symbols=False)
    with pytest.raises(ValueError):
        generate_password(options)


def test_generate_password_zero_length_raises():
    with pytest.raises(ValueError):
        generate_password(PasswordOptions(length=0))


def test_generate_password_exclude_ambiguous():
    options = PasswordOptions(length=200, exclude_ambiguous=True)
    value = generate_password(options)
    assert not any(c in "il1Lo0O" for c in value)


def test_generate_passphrase_word_count_and_separator():
    value = generate_passphrase(word_count=5, separator="_")
    assert len(value.split("_")) == 5


def test_generate_passphrase_capitalize():
    value = generate_passphrase(word_count=3, capitalize=True)
    for word in value.split("-"):
        assert word[0].isupper()


def test_generate_passphrase_invalid_word_count_raises():
    with pytest.raises(ValueError):
        generate_passphrase(word_count=0)


def test_password_entropy_bits_zero_pool():
    assert password_entropy_bits(10, 0) == 0.0


def test_password_entropy_bits_increases_with_length():
    assert password_entropy_bits(20, 26) > password_entropy_bits(10, 26)


def test_strength_label_thresholds():
    assert strength_label(10) == "Very Weak"
    assert strength_label(30) == "Weak"
    assert strength_label(50) == "Fair"
    assert strength_label(100) == "Strong"
    assert strength_label(150) == "Very Strong"
