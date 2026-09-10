"""Central registry of available tools. The UI never hard-codes tool lists."""

from __future__ import annotations

from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, type[ToolWidget]] = {}

    def register(self, tool_cls: type[ToolWidget]) -> type[ToolWidget]:
        meta = tool_cls.metadata
        if meta.id in self._tools:
            raise ValueError(f"Tool id already registered: {meta.id}")
        self._tools[meta.id] = tool_cls
        return tool_cls

    def get_by_id(self, tool_id: str) -> type[ToolWidget] | None:
        return self._tools.get(tool_id)

    def get_all(self) -> list[ToolMetadata]:
        return sorted((cls.metadata for cls in self._tools.values()), key=lambda m: m.name)

    def get_by_category(self, category: str) -> list[ToolMetadata]:
        return sorted(
            (cls.metadata for cls in self._tools.values() if cls.metadata.category == category),
            key=lambda m: m.name,
        )

    def categories(self) -> list[str]:
        return sorted({cls.metadata.category for cls in self._tools.values()})

    def search(self, query: str) -> list[ToolMetadata]:
        query = query.strip().lower()
        if not query:
            return self.get_all()

        results: list[tuple[int, ToolMetadata]] = []
        for cls in self._tools.values():
            meta = cls.metadata
            score = self._match_score(query, meta)
            if score > 0:
                results.append((score, meta))
        results.sort(key=lambda pair: (-pair[0], pair[1].name))
        return [meta for _, meta in results]

    @staticmethod
    def _match_score(query: str, meta: ToolMetadata) -> int:
        name = meta.name.lower()
        if query == name:
            return 100
        if name.startswith(query):
            return 80
        if query in name:
            return 60
        if any(query == kw.lower() for kw in meta.keywords):
            return 50
        if any(query in kw.lower() for kw in meta.keywords):
            return 30
        if query in meta.category.lower():
            return 20
        if query in meta.description.lower():
            return 10
        return 0
