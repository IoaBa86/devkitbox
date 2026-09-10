"""Pure password/passphrase generation logic — no Qt imports, fully unit-testable."""

from __future__ import annotations

import math
import secrets
import string

LOWERCASE = string.ascii_lowercase
UPPERCASE = string.ascii_uppercase
DIGITS = string.digits
SYMBOLS = "!@#$%^&*()-_=+[]{};:,.<>?/"
AMBIGUOUS = "il1Lo0O"

WORDLIST = [
    "apple",
    "brave",
    "cider",
    "delta",
    "ember",
    "flint",
    "grove",
    "haven",
    "ionic",
    "jolly",
    "karma",
    "lemon",
    "mango",
    "noble",
    "onyx",
    "pearl",
    "quiet",
    "raven",
    "solar",
    "tiger",
    "umbra",
    "vivid",
    "willow",
    "xenon",
    "yield",
    "zebra",
    "amber",
    "birch",
    "coral",
    "dusk",
    "echo",
    "forge",
    "glow",
    "harbor",
    "ivy",
    "jade",
    "kite",
    "lunar",
    "maple",
    "nova",
    "opal",
    "pine",
    "quartz",
    "ridge",
    "slate",
    "thorn",
    "urban",
    "vale",
    "wren",
]


class PasswordOptions:
    def __init__(
        self,
        length: int = 16,
        lowercase: bool = True,
        uppercase: bool = True,
        digits: bool = True,
        symbols: bool = True,
        exclude_ambiguous: bool = False,
    ) -> None:
        self.length = length
        self.lowercase = lowercase
        self.uppercase = uppercase
        self.digits = digits
        self.symbols = symbols
        self.exclude_ambiguous = exclude_ambiguous


def _char_pool(options: PasswordOptions) -> str:
    pool = ""
    if options.lowercase:
        pool += LOWERCASE
    if options.uppercase:
        pool += UPPERCASE
    if options.digits:
        pool += DIGITS
    if options.symbols:
        pool += SYMBOLS
    if options.exclude_ambiguous:
        pool = "".join(c for c in pool if c not in AMBIGUOUS)
    return pool


def generate_password(options: PasswordOptions) -> str:
    pool = _char_pool(options)
    if not pool:
        raise ValueError("At least one character set must be selected")
    if options.length < 1:
        raise ValueError("Length must be at least 1")

    required: list[str] = []
    for enabled, charset in (
        (options.lowercase, LOWERCASE),
        (options.uppercase, UPPERCASE),
        (options.digits, DIGITS),
        (options.symbols, SYMBOLS),
    ):
        if not enabled:
            continue
        charset = (
            "".join(c for c in charset if c not in AMBIGUOUS)
            if options.exclude_ambiguous
            else charset
        )
        if charset:
            required.append(secrets.choice(charset))

    remaining = max(options.length - len(required), 0)
    chars = required + [secrets.choice(pool) for _ in range(remaining)]
    chars = chars[: options.length]
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def generate_passphrase(word_count: int = 4, separator: str = "-", capitalize: bool = False) -> str:
    if word_count < 1:
        raise ValueError("Word count must be at least 1")
    words = [secrets.choice(WORDLIST) for _ in range(word_count)]
    if capitalize:
        words = [w.capitalize() for w in words]
    return separator.join(words)


def password_entropy_bits(length: int, pool_size: int) -> float:
    if pool_size <= 0 or length <= 0:
        return 0.0
    return length * math.log2(pool_size)


def strength_label(entropy_bits: float) -> str:
    if entropy_bits < 28:
        return "Very Weak"
    if entropy_bits < 36:
        return "Weak"
    if entropy_bits < 60:
        return "Fair"
    if entropy_bits < 128:
        return "Strong"
    return "Very Strong"
