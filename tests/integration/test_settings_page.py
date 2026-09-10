"""Widget-level tests for the Settings page's Network/Updates/About tabs —
these were previously static placeholder text with no real behavior."""

from __future__ import annotations

from app.ui.pages.settings_page import SettingsPage


def test_network_tab_timeout_persists(qtbot, context):
    page = SettingsPage(context)
    qtbot.addWidget(page)

    page._timeout_spin.setValue(90)

    assert context.settings.request_timeout_seconds == 90
    assert context.settings_service.load().request_timeout_seconds == 90


def test_network_tab_proxy_persists(qtbot, context):
    page = SettingsPage(context)
    qtbot.addWidget(page)

    page._proxy_edit.setText("http://proxy.example.com:8080")
    page._proxy_edit.editingFinished.emit()

    assert context.settings.http_proxy_url == "http://proxy.example.com:8080"
    assert context.settings_service.load().http_proxy_url == "http://proxy.example.com:8080"


def test_network_tab_verify_ssl_persists(qtbot, context):
    page = SettingsPage(context)
    qtbot.addWidget(page)

    page._verify_ssl_check.setChecked(False)

    assert context.settings.verify_ssl_certificates is False
    assert context.settings_service.load().verify_ssl_certificates is False


def test_updates_tab_shows_current_version(qtbot, context):
    from PySide6.QtWidgets import QLabel

    from app.core.constants import APP_VERSION

    page = SettingsPage(context)
    qtbot.addWidget(page)

    labels = [label.text() for label in page.findChildren(QLabel)]
    assert any(APP_VERSION in text for text in labels)


def test_settings_page_constructs_without_error(qtbot, context):
    page = SettingsPage(context)
    qtbot.addWidget(page)
    assert page is not None
