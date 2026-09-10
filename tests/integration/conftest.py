from __future__ import annotations

import logging

import pytest

from app.core.app_context import AppContext
from app.main import _register_tools


@pytest.fixture
def context(tmp_path, monkeypatch):
    monkeypatch.setattr("app.core.app_context.get_db_path", lambda: tmp_path / "test.db")
    ctx = AppContext(logging.getLogger("test"))
    _register_tools(ctx)
    yield ctx
    ctx.database.close()
