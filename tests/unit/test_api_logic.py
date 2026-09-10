from __future__ import annotations

import io
import urllib.error
import urllib.request
from unittest.mock import patch

import pytest

from app.core.exceptions import NetworkError, ValidationError
from app.tools.api.logic import (
    ApiRequest,
    ApiResponse,
    build_request,
    format_response_body,
    parse_headers_text,
    send_request,
)


def test_parse_headers_text_basic():
    headers = parse_headers_text("Content-Type: application/json\nAuthorization: Bearer abc")
    assert headers == {"Content-Type": "application/json", "Authorization": "Bearer abc"}


def test_parse_headers_text_skips_blank_lines():
    assert parse_headers_text("\n\nX-Test: 1\n\n") == {"X-Test": "1"}


def test_parse_headers_text_invalid_line_raises():
    with pytest.raises(ValidationError):
        parse_headers_text("not-a-header-line")


def test_build_request_valid():
    request = build_request("get", "https://example.com", {}, "")
    assert request.method == "GET"
    assert request.url == "https://example.com"


def test_build_request_unsupported_method_raises():
    with pytest.raises(ValidationError):
        build_request("TRACE", "https://example.com", {}, "")


def test_build_request_empty_url_raises():
    with pytest.raises(ValidationError):
        build_request("GET", "  ", {}, "")


def test_build_request_missing_scheme_raises():
    with pytest.raises(ValidationError):
        build_request("GET", "example.com", {}, "")


class _FakeResponse:
    def __init__(self, body: bytes, status: int, reason: str, headers: dict[str, str]) -> None:
        self._body = body
        self.status = status
        self.reason = reason
        self.headers = headers

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, *args: object) -> None:
        return None


def test_send_request_success():
    request = ApiRequest(method="GET", url="https://example.com", headers={}, body="")
    fake_response = _FakeResponse(b'{"ok": true}', 200, "OK", {"Content-Type": "application/json"})

    with patch("urllib.request.urlopen", return_value=fake_response):
        response = send_request(request)

    assert response.status_code == 200
    assert response.reason == "OK"
    assert response.body == '{"ok": true}'
    assert response.elapsed_ms >= 0


def test_send_request_http_error_returns_response():
    request = ApiRequest(method="GET", url="https://example.com", headers={}, body="")
    http_error = urllib.error.HTTPError(
        "https://example.com",
        404,
        "Not Found",
        {"Content-Type": "text/plain"},
        io.BytesIO(b"missing"),
    )

    with patch("urllib.request.urlopen", side_effect=http_error):
        response = send_request(request)

    assert response.status_code == 404
    assert response.body == "missing"


def test_send_request_url_error_raises_network_error():
    request = ApiRequest(method="GET", url="https://example.com", headers={}, body="")
    url_error = urllib.error.URLError("connection refused")

    with patch("urllib.request.urlopen", side_effect=url_error), pytest.raises(NetworkError):
        send_request(request)


def test_format_response_body_pretty_prints_json():
    response = ApiResponse(
        status_code=200,
        reason="OK",
        headers={"Content-Type": "application/json"},
        body='{"a":1}',
        elapsed_ms=1.0,
    )
    assert format_response_body(response) == '{\n  "a": 1\n}'


def test_send_request_uses_proxy_when_configured():
    request = ApiRequest(method="GET", url="https://example.com", headers={}, body="")
    fake_response = _FakeResponse(b"ok", 200, "OK", {})

    captured = {}

    class _FakeOpener:
        def urlopen(self, req, timeout=None):
            captured["timeout"] = timeout
            return fake_response

    def fake_build_opener(*handlers):
        captured["handlers"] = handlers
        return _FakeOpener()

    with patch("urllib.request.build_opener", side_effect=fake_build_opener):
        response = send_request(request, timeout=5, proxy_url="http://proxy:8080")

    assert response.status_code == 200
    assert len(captured["handlers"]) == 1
    assert captured["timeout"] == 5


def test_send_request_no_proxy_no_handlers_uses_plain_urlopen():
    request = ApiRequest(method="GET", url="https://example.com", headers={}, body="")
    fake_response = _FakeResponse(b"ok", 200, "OK", {})

    with (
        patch("urllib.request.build_opener") as mock_build_opener,
        patch("urllib.request.urlopen", return_value=fake_response),
    ):
        response = send_request(request)

    mock_build_opener.assert_not_called()
    assert response.status_code == 200


def test_send_request_verify_ssl_false_adds_https_handler():
    request = ApiRequest(method="GET", url="https://example.com", headers={}, body="")
    fake_response = _FakeResponse(b"ok", 200, "OK", {})

    captured = {}

    class _FakeOpener:
        def urlopen(self, req, timeout=None):
            return fake_response

    def fake_build_opener(*handlers):
        captured["handlers"] = handlers
        return _FakeOpener()

    with patch("urllib.request.build_opener", side_effect=fake_build_opener):
        send_request(request, verify_ssl=False)

    assert len(captured["handlers"]) == 1
    assert isinstance(captured["handlers"][0], urllib.request.HTTPSHandler)


def test_format_response_body_non_json_passthrough():
    response = ApiResponse(
        status_code=200,
        reason="OK",
        headers={"Content-Type": "text/plain"},
        body="hi",
        elapsed_ms=1.0,
    )
    assert format_response_body(response) == "hi"
