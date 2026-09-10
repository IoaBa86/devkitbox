"""Tool metadata model used by the registry, search, and navigation."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ToolMetadata:
    """Static description of a tool, independent of its widget implementation."""

    id: str
    name: str
    description: str
    category: str
    keywords: tuple[str, ...] = field(default_factory=tuple)
    icon: str = ""
    shortcut: str | None = None
