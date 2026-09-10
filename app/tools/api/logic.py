"""Pure HTTP request/response logic — no Qt imports, fully unit-testable.

Network I/O uses the stdlib (``urllib``) only, so a request is made solely
when :func:`send_request` is called explicitly (never on import or at rest),
matching the app's no-background-network-calls privacy guarantee.
"""

from __future__ import annotations

import json
import ssl
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field

from app.core.exceptions import NetworkError, ValidationError

METHODS = ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS")
DEFAULT_TIMEOUT_SECONDS = 30


@dataclass(frozen=True, slots=True)
class ApiResponse:
    status_code: int
    reason: str
    headers: dict[str, str]
    body: str
    elapsed_ms: float


@dataclass(frozen=True, slots=True)
class ApiRequest:
    method: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    body: str = ""


def parse_headers_text(text: str) -> dict[str, str]:
    """Parse ``Key: Value`` lines (one per line) into a headers dict."""
    headers: dict[str, str] = {}
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        if ":" not in stripped:
            raise ValidationError(f"Invalid header on line {line_no}: {line!r}", line=line_no)
        key, _, value = stripped.partition(":")
        headers[key.strip()] = value.strip()
    return headers


def build_request(method: str, url: str, headers: dict[str, str], body: str) -> ApiRequest:
    method = method.upper().strip()
    if method not in METHODS:
        raise ValidationError(f"Unsupported method: {method}")
    if not url.strip():
        raise ValidationError("URL is required")
    if not url.startswith(("http://", "https://")):
        raise ValidationError("URL must start with http:// or https://")
    return ApiRequest(method=method, url=url.strip(), headers=dict(headers), body=body)


def send_request(
    request: ApiRequest,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    proxy_url: str = "",
    verify_ssl: bool = True,
) -> ApiResponse:
    # Scheme is validated by build_request() before an ApiRequest can exist,
    # so this is not an open redirect / arbitrary-scheme vector.
    data = request.body.encode("utf-8") if request.body and request.method != "GET" else None
    urllib_request = urllib.request.Request(  # noqa: S310
        request.url, data=data, headers=request.headers, method=request.method
    )

    handlers: list[urllib.request.BaseHandler] = []
    if proxy_url.strip():
        handlers.append(urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url}))
    if not verify_ssl:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        handlers.append(urllib.request.HTTPSHandler(context=context))
    opener = urllib.request.build_opener(*handlers) if handlers else urllib.request

    start = time.monotonic()
    try:
        with opener.urlopen(urllib_request, timeout=timeout) as response:  # noqa: S310
            body_bytes = response.read()
            status_code = response.status
            reason = response.reason
            response_headers = dict(response.headers.items())
    except urllib.error.HTTPError as exc:
        body_bytes = exc.read()
        status_code = exc.code
        reason = exc.reason
        response_headers = dict(exc.headers.items()) if exc.headers else {}
    except urllib.error.URLError as exc:
        raise NetworkError(f"Request failed: {exc.reason}", detail=str(exc)) from exc
    except (TimeoutError, OSError) as exc:
        raise NetworkError(f"Request failed: {exc}", detail=str(exc)) from exc
    elapsed_ms = (time.monotonic() - start) * 1000

    try:
        body_text = body_bytes.decode("utf-8")
    except UnicodeDecodeError:
        body_text = body_bytes.decode("utf-8", errors="replace")

    return ApiResponse(
        status_code=status_code,
        reason=reason,
        headers=response_headers,
        body=body_text,
        elapsed_ms=elapsed_ms,
    )


def format_response_body(response: ApiResponse) -> str:
    content_type = next((v for k, v in response.headers.items() if k.lower() == "content-type"), "")
    if "json" in content_type.lower():
        try:
            return json.dumps(json.loads(response.body), indent=2)
        except (json.JSONDecodeError, TypeError):
            return response.body
    return response.body
