from __future__ import annotations

import pytest

from app.services.database import DatabaseService
from app.services.settings_service import SettingsService


@pytest.fixture
def settings_service(tmp_path):
    db = DatabaseService(tmp_path / "test.db")
    db.connect()
    yield SettingsService(db)
    db.close()


def test_load_returns_defaults_when_empty(settings_service):
    settings = settings_service.load()
    assert settings.theme == "dark"
    assert settings.tool_history_enabled is False


def test_set_and_load_roundtrip(settings_service):
    settings_service.set("theme", "light")
    settings_service.set("editor_font_size", 16)
    settings_service.set("tool_history_enabled", True)

    settings = settings_service.load()
    assert settings.theme == "light"
    assert settings.editor_font_size == 16
    assert settings.tool_history_enabled is True


def test_onboarding_flag_defaults_false_and_persists(settings_service):
    assert settings_service.load().has_completed_onboarding is False

    settings_service.set("has_completed_onboarding", True)

    assert settings_service.load().has_completed_onboarding is True


def test_clipboard_history_enabled_roundtrip(settings_service):
    settings_service.set("clipboard_history_enabled", True)
    assert settings_service.load().clipboard_history_enabled is True


def test_network_settings_defaults(settings_service):
    settings = settings_service.load()
    assert settings.request_timeout_seconds == 30
    assert settings.http_proxy_url == ""
    assert settings.verify_ssl_certificates is True


def test_network_settings_roundtrip(settings_service):
    settings_service.set("request_timeout_seconds", 60)
    settings_service.set("http_proxy_url", "http://proxy:8080")
    settings_service.set("verify_ssl_certificates", False)

    settings = settings_service.load()
    assert settings.request_timeout_seconds == 60
    assert settings.http_proxy_url == "http://proxy:8080"
    assert settings.verify_ssl_certificates is False


def test_set_unknown_key_raises(settings_service):
    with pytest.raises(KeyError):
        settings_service.set("not_a_real_setting", "value")


def test_save_persists_all_fields(settings_service):
    settings = settings_service.load()
    settings.theme = "system"
    settings.minimize_to_tray = True
    settings_service.save(settings)

    reloaded = settings_service.load()
    assert reloaded.theme == "system"
    assert reloaded.minimize_to_tray is True
