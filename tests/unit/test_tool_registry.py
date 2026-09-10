from __future__ import annotations

import pytest

from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.registry import ToolRegistry


def _make_tool(
    tool_id: str, name: str, category: str, keywords: tuple[str, ...]
) -> type[ToolWidget]:
    metadata = ToolMetadata(
        id=tool_id,
        name=name,
        description=f"{name} description",
        category=category,
        keywords=keywords,
    )

    class _DummyTool(ToolWidget):
        pass

    _DummyTool.metadata = metadata
    _DummyTool.__name__ = f"Dummy_{tool_id}"
    return _DummyTool


@pytest.fixture
def registry():
    reg = ToolRegistry()
    reg.register(_make_tool("json_formatter", "JSON Formatter", "Development", ("json", "format")))
    reg.register(_make_tool("jwt_decoder", "JWT Decoder", "Development", ("jwt", "token")))
    reg.register(_make_tool("hash_generator", "Hash Generator", "Encoding", ("hash", "sha")))
    return reg


def test_register_duplicate_id_raises(registry):
    dup = _make_tool("json_formatter", "JSON Formatter 2", "Development", ())
    with pytest.raises(ValueError):
        registry.register(dup)


def test_get_by_id(registry):
    assert registry.get_by_id("jwt_decoder").metadata.name == "JWT Decoder"
    assert registry.get_by_id("missing") is None


def test_get_by_category(registry):
    dev_tools = registry.get_by_category("Development")
    assert [m.id for m in dev_tools] == ["json_formatter", "jwt_decoder"]


def test_categories(registry):
    assert registry.categories() == ["Development", "Encoding"]


def test_search_exact_and_keyword_matches(registry):
    results = registry.search("json")
    assert results[0].id == "json_formatter"

    results = registry.search("jwt")
    assert results[0].id == "jwt_decoder"

    results = registry.search("hash")
    assert results[0].id == "hash_generator"


def test_search_empty_query_returns_all_sorted_by_name(registry):
    results = registry.search("")
    assert [m.id for m in results] == ["hash_generator", "json_formatter", "jwt_decoder"]


def test_search_no_match_returns_empty(registry):
    assert registry.search("nonexistent") == []
