from __future__ import annotations

from unittest.mock import patch

import pytest

from app.core.exceptions import NetworkError
from app.tools.api.logic import ApiResponse
from app.services.update_service import (
    check_for_update,
    is_newer_version,
    parse_version,
)


def test_parse_version_basic():
    assert parse_version("1.2.3") == (1, 2, 3)


def test_parse_version_with_v_prefix():
    assert parse_version("v1.2.3") == (1, 2, 3)


def test_parse_version_unparseable_returns_none():
    assert parse_version("not-a-version") is None


def test_is_newer_version_true():
    assert is_newer_version("1.0.0", "1.2.0") is True


def test_is_newer_version_false_when_equal():
    assert is_newer_version("1.0.0", "1.0.0") is False


def test_is_newer_version_false_when_older():
    assert is_newer_version("2.0.0", "1.9.9") is False


def _fake_response(body: str, status: int = 200) -> ApiResponse:
    return ApiResponse(status_code=status, reason="OK", headers={}, body=body, elapsed_ms=1.0)


def test_check_for_update_reports_update_available():
    body = '{"tag_name": "v9.9.9", "html_url": "https://example.com/releases/v9.9.9"}'
    with patch("app.services.update_service.send_request", return_value=_fake_response(body)):
        result = check_for_update()

    assert result.is_update_available is True
    assert result.latest_version == "9.9.9"
    assert result.release_url == "https://example.com/releases/v9.9.9"


def test_check_for_update_reports_up_to_date():
    from app.core.constants import APP_VERSION

    body = f'{{"tag_name": "v{APP_VERSION}"}}'
    with patch("app.services.update_service.send_request", return_value=_fake_response(body)):
        result = check_for_update()

    assert result.is_update_available is False


def test_check_for_update_non_200_raises_network_error():
    with (
        patch(
            "app.services.update_service.send_request",
            return_value=_fake_response("", status=403),
        ),
        pytest.raises(NetworkError),
    ):
        check_for_update()


def test_check_for_update_404_raises_friendly_network_error():
    with (
        patch(
            "app.services.update_service.send_request",
            return_value=_fake_response("", status=404),
        ),
        pytest.raises(NetworkError, match="No release has been published yet"),
    ):
        check_for_update()


def test_check_for_update_invalid_json_raises_network_error():
    with (
        patch("app.services.update_service.send_request", return_value=_fake_response("not json")),
        pytest.raises(NetworkError),
    ):
        check_for_update()


def test_check_for_update_missing_tag_name_raises_network_error():
    with (
        patch("app.services.update_service.send_request", return_value=_fake_response("{}")),
        pytest.raises(NetworkError),
    ):
        check_for_update()
