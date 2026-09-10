"""Pure cookie string parsing logic — no Qt imports, fully unit-testable."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.core.exceptions import ValidationError

_KNOWN_ATTRIBUTES = {
    "expires",
    "max-age",
    "domain",
    "path",
    "samesite",
}
_FLAG_ATTRIBUTES = {"secure", "httponly", "partitioned"}


@dataclass(frozen=True, slots=True)
class SetCookieInfo:
    name: str
    value: str
    domain: str | None
    path: str | None
    expires: str | None
    max_age: str | None
    same_site: str | None
    secure: bool
    http_only: bool
    attributes: dict[str, str] = field(default_factory=dict)


def parse_set_cookie(header: str) -> SetCookieInfo:
    parts = [p.strip() for p in header.strip().split(";") if p.strip()]
    if not parts:
        raise ValidationError("Enter a Set-Cookie header value")

    name_value = parts[0]
    if "=" not in name_value:
        raise ValidationError("First segment must be name=value")
    name, value = name_value.split("=", 1)
    name = name.strip()
    if not name:
        raise ValidationError("Cookie name cannot be empty")

    domain = path = expires = max_age = same_site = None
    secure = http_only = False
    extra: dict[str, str] = {}

    for part in parts[1:]:
        if "=" in part:
            attr_name, attr_value = part.split("=", 1)
        else:
            attr_name, attr_value = part, ""
        key = attr_name.strip().lower()
        attr_value = attr_value.strip()

        if key == "domain":
            domain = attr_value
        elif key == "path":
            path = attr_value
        elif key == "expires":
            expires = attr_value
        elif key == "max-age":
            max_age = attr_value
        elif key == "samesite":
            same_site = attr_value
        elif key == "secure":
            secure = True
        elif key == "httponly":
            http_only = True
        elif key not in _FLAG_ATTRIBUTES:
            extra[attr_name.strip()] = attr_value

    return SetCookieInfo(
        name=name,
        value=value.strip(),
        domain=domain,
        path=path,
        expires=expires,
        max_age=max_age,
        same_site=same_site,
        secure=secure,
        http_only=http_only,
        attributes=extra,
    )


def parse_cookie_header(header: str) -> dict[str, str]:
    """Parse a client-sent ``Cookie`` request header: ``name1=value1; name2=value2``."""
    result: dict[str, str] = {}
    for part in header.strip().split(";"):
        part = part.strip()
        if not part or "=" not in part:
            continue
        name, value = part.split("=", 1)
        result[name.strip()] = value.strip()
    return result
