"""Pure User-Agent string parsing logic — no Qt imports, fully unit-testable.

Heuristic, regex-based — covers the common browsers/OSes/devices well
enough for a devtool, but (like every from-scratch UA parser) won't match
a full UA-database library on obscure or spoofed strings.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.core.exceptions import ValidationError

_BOT_MARKERS = (
    "bot",
    "crawler",
    "spider",
    "slurp",
    "bingpreview",
    "googlebot",
    "facebookexternalhit",
    "curl",
    "wget",
    "python-requests",
    "postmanruntime",
)

# Order matters: Edge/Opera UAs also contain "Chrome/", Chrome UAs also
# contain "Safari/" — so the more specific token must be checked first.
_BROWSER_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("Edge", re.compile(r"Edg(?:A|iOS)?/(?P<version>[\d.]+)")),
    ("Opera", re.compile(r"(?:OPR|Opera)/(?P<version>[\d.]+)")),
    ("Samsung Internet", re.compile(r"SamsungBrowser/(?P<version>[\d.]+)")),
    ("Firefox", re.compile(r"Firefox/(?P<version>[\d.]+)")),
    ("Chrome", re.compile(r"Chrome/(?P<version>[\d.]+)")),
    ("Safari", re.compile(r"Version/(?P<version>[\d.]+).*Safari/")),
    ("Internet Explorer", re.compile(r"MSIE (?P<version>[\d.]+)")),
    ("Internet Explorer", re.compile(r"rv:(?P<version>[\d.]+)\).*like Gecko")),
)

_OS_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("Windows", re.compile(r"Windows NT (?P<version>[\d.]+)")),
    ("iOS", re.compile(r"(?:iPhone|iPad|iPod).*OS (?P<version>[\d_]+)")),
    ("macOS", re.compile(r"Mac OS X (?P<version>[\d_]+)")),
    ("Android", re.compile(r"Android (?P<version>[\d.]+)")),
    ("Linux", re.compile(r"Linux")),
    ("Chrome OS", re.compile(r"CrOS")),
)


@dataclass(frozen=True, slots=True)
class UserAgentInfo:
    browser: str | None
    browser_version: str | None
    os: str | None
    os_version: str | None
    device_type: str
    is_bot: bool
    raw: str


def parse_user_agent(user_agent: str) -> UserAgentInfo:
    text = user_agent.strip()
    if not text:
        raise ValidationError("Enter a User-Agent string")

    lower = text.lower()
    is_bot = any(marker in lower for marker in _BOT_MARKERS)

    browser = browser_version = None
    for name, pattern in _BROWSER_PATTERNS:
        match = pattern.search(text)
        if match:
            browser = name
            browser_version = match.group("version")
            break

    os_name = os_version = None
    for name, pattern in _OS_PATTERNS:
        match = pattern.search(text)
        if match:
            os_name = name
            os_version = match.groupdict().get("version", "").replace("_", ".") or None
            break

    if "iPad" in text or ("Android" in text and "Mobile" not in text):
        device_type = "Tablet"
    elif "Mobile" in text or "iPhone" in text or "Android" in text:
        device_type = "Mobile"
    else:
        device_type = "Desktop"

    return UserAgentInfo(
        browser=browser,
        browser_version=browser_version,
        os=os_name,
        os_version=os_version,
        device_type=device_type,
        is_bot=is_bot,
        raw=text,
    )
