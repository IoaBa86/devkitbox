"""Manual update check against GitHub Releases.

A request is made only when :func:`check_for_update` is called explicitly
(e.g. by pressing "Check for Updates" in Settings), matching the app's
no-background-network-calls privacy guarantee — see app/tools/api/logic.py.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from urllib.parse import urlparse

from app.core.constants import APP_NAME, APP_VERSION, GITHUB_URL
from app.core.exceptions import NetworkError, ValidationError
from app.tools.api.logic import ApiRequest, send_request

_VERSION_RE = re.compile(r"(\d+)\.(\d+)\.(\d+)")


@dataclass(frozen=True, slots=True)
class UpdateCheckResult:
    current_version: str
    latest_version: str
    is_update_available: bool
    release_url: str


def _repo_releases_api_url() -> str:
    if not GITHUB_URL:
        raise ValidationError("No GitHub repository is configured")
    owner_repo = urlparse(GITHUB_URL).path.strip("/")
    if not owner_repo:
        raise ValidationError("GitHub repository URL is malformed")
    return f"https://api.github.com/repos/{owner_repo}/releases/latest"


def parse_version(version: str) -> tuple[int, int, int] | None:
    match = _VERSION_RE.search(version)
    if not match:
        return None
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)))


def is_newer_version(current: str, latest: str) -> bool:
    current_parsed = parse_version(current)
    latest_parsed = parse_version(latest)
    if current_parsed is None or latest_parsed is None:
        return latest.strip().lstrip("vV") != current.strip().lstrip("vV")
    return latest_parsed > current_parsed


def check_for_update(
    timeout: float = 10,
    proxy_url: str = "",
    verify_ssl: bool = True,
) -> UpdateCheckResult:
    request = ApiRequest(
        method="GET",
        url=_repo_releases_api_url(),
        headers={"Accept": "application/vnd.github+json", "User-Agent": APP_NAME},
    )
    response = send_request(request, timeout=timeout, proxy_url=proxy_url, verify_ssl=verify_ssl)
    if response.status_code != 200:
        raise NetworkError(f"GitHub returned {response.status_code} {response.reason}")

    try:
        payload = json.loads(response.body)
    except json.JSONDecodeError as exc:
        raise NetworkError("GitHub response was not valid JSON") from exc

    tag_name = payload.get("tag_name")
    if not tag_name:
        raise NetworkError("GitHub release response had no tag_name")

    latest_version = tag_name.lstrip("vV")
    return UpdateCheckResult(
        current_version=APP_VERSION,
        latest_version=latest_version,
        is_update_available=is_newer_version(APP_VERSION, latest_version),
        release_url=payload.get("html_url", GITHUB_URL or ""),
    )
