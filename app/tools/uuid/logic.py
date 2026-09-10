"""Pure UUID generation/formatting logic — no Qt imports, fully unit-testable."""

from __future__ import annotations

import uuid

NAMESPACE_PRESETS: dict[str, uuid.UUID] = {
    "DNS": uuid.NAMESPACE_DNS,
    "URL": uuid.NAMESPACE_URL,
    "OID": uuid.NAMESPACE_OID,
    "X500": uuid.NAMESPACE_X500,
}


def generate_v1() -> uuid.UUID:
    return uuid.uuid1()


def generate_v4() -> uuid.UUID:
    return uuid.uuid4()


def generate_v5(namespace: uuid.UUID, name: str) -> uuid.UUID:
    return uuid.uuid5(namespace, name)


def generate_bulk(
    version: int, count: int, namespace: uuid.UUID | None = None, name: str = ""
) -> list[uuid.UUID]:
    if version == 1:
        return [generate_v1() for _ in range(count)]
    if version == 4:
        return [generate_v4() for _ in range(count)]
    if version == 5:
        ns = namespace or uuid.NAMESPACE_DNS
        return [generate_v5(ns, f"{name}-{i}" if count > 1 else name) for i in range(count)]
    raise ValueError(f"Unsupported UUID version: {version}")


def format_uuid(
    value: uuid.UUID, uppercase: bool = False, braces: bool = False, hyphens: bool = True
) -> str:
    text = str(value)
    if not hyphens:
        text = text.replace("-", "")
    if uppercase:
        text = text.upper()
    if braces:
        text = f"{{{text}}}"
    return text
