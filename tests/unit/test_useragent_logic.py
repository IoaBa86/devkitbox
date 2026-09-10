from __future__ import annotations

import pytest

from app.core.exceptions import ValidationError
from app.tools.useragent.logic import parse_user_agent

CHROME_WINDOWS = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/128.0.0.0 Safari/537.36"
)
FIREFOX_LINUX = "Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0"
SAFARI_MAC = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/17.5 Safari/605.1.15"
)
SAFARI_IPHONE = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1"
)
EDGE_WINDOWS = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0"
)
CHROME_ANDROID = (
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/128.0.0.0 Mobile Safari/537.36"
)
GOOGLEBOT = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"


def test_parse_chrome_windows():
    info = parse_user_agent(CHROME_WINDOWS)
    assert info.browser == "Chrome"
    assert info.browser_version == "128.0.0.0"
    assert info.os == "Windows"
    assert info.os_version == "10.0"
    assert info.device_type == "Desktop"
    assert info.is_bot is False


def test_parse_firefox_linux():
    info = parse_user_agent(FIREFOX_LINUX)
    assert info.browser == "Firefox"
    assert info.browser_version == "130.0"
    assert info.os == "Linux"


def test_parse_safari_mac():
    info = parse_user_agent(SAFARI_MAC)
    assert info.browser == "Safari"
    assert info.browser_version == "17.5"
    assert info.os == "macOS"
    assert info.os_version == "10.15.7"


def test_parse_safari_iphone_is_mobile():
    info = parse_user_agent(SAFARI_IPHONE)
    assert info.browser == "Safari"
    assert info.os == "iOS"
    assert info.device_type == "Mobile"


def test_parse_edge_not_confused_with_chrome():
    info = parse_user_agent(EDGE_WINDOWS)
    assert info.browser == "Edge"


def test_parse_chrome_android_is_mobile():
    info = parse_user_agent(CHROME_ANDROID)
    assert info.browser == "Chrome"
    assert info.os == "Android"
    assert info.device_type == "Mobile"


def test_parse_googlebot_is_bot():
    info = parse_user_agent(GOOGLEBOT)
    assert info.is_bot is True


def test_parse_empty_raises():
    with pytest.raises(ValidationError):
        parse_user_agent("")


def test_parse_unknown_string_no_crash():
    info = parse_user_agent("something-unrecognizable/1.0")
    assert info.browser is None
    assert info.os is None
    assert info.device_type == "Desktop"
