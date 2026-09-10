"""Settings: Appearance, Network, Privacy, Updates, About. Editor/Behavior tabs land later."""

from __future__ import annotations

import os
import subprocess
import sys

from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.core.app_context import AppContext
from app.core.constants import APP_DISPLAY_NAME, APP_TAGLINE, APP_VERSION, GITHUB_URL, WEBSITE_URL
from app.core.exceptions import DevKitBoxError
from app.core.paths import get_log_dir
from app.services.update_service import UpdateCheckResult, check_for_update

_ACCENT_PRESETS = {
    "Violet": "#7C5CFF",
    "Blue": "#4C8DFF",
    "Emerald": "#34D399",
    "Amber": "#FFB454",
    "Coral": "#FF6B6B",
}


class _UpdateCheckWorker(QObject):
    finished = Signal(object)
    failed = Signal(str)

    def __init__(self, timeout: float, proxy_url: str, verify_ssl: bool) -> None:
        super().__init__()
        self._timeout = timeout
        self._proxy_url = proxy_url
        self._verify_ssl = verify_ssl

    def run(self) -> None:
        try:
            result = check_for_update(self._timeout, self._proxy_url, self._verify_ssl)
        except DevKitBoxError as exc:
            self.failed.emit(exc.message)
            return
        self.finished.emit(result)


class SettingsPage(QWidget):
    theme_changed = Signal()

    def __init__(self, context: AppContext, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.context = context

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        title = QLabel("Settings")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        tabs = QTabWidget()
        tabs.addTab(self._build_appearance_tab(), "Appearance")
        tabs.addTab(self._build_network_tab(), "Network")
        tabs.addTab(self._build_privacy_tab(), "Privacy")
        tabs.addTab(self._build_updates_tab(), "Updates")
        tabs.addTab(self._build_about_tab(), "About")
        layout.addWidget(tabs, stretch=1)

    def _build_appearance_tab(self) -> QWidget:
        tab = QWidget()
        form = QFormLayout(tab)

        theme_row = QHBoxLayout()
        self._theme_group = QButtonGroup(tab)
        for label, value in (("Light", "light"), ("Dark", "dark"), ("System", "system")):
            radio = QRadioButton(label)
            radio.setChecked(self.context.settings.theme == value)
            radio.toggled.connect(lambda checked, v=value: checked and self._on_theme_changed(v))
            self._theme_group.addButton(radio)
            theme_row.addWidget(radio)
        form.addRow("Theme", theme_row)

        accent_combo = QComboBox()
        accent_combo.addItems(list(_ACCENT_PRESETS.keys()))
        current_name = next(
            (n for n, c in _ACCENT_PRESETS.items() if c == self.context.settings.accent_color),
            "Violet",
        )
        accent_combo.setCurrentText(current_name)
        accent_combo.currentTextChanged.connect(self._on_accent_changed)
        form.addRow("Accent color", accent_combo)

        return tab

    def _build_network_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)

        intro = QLabel(
            "Local developer tools do not require an internet connection. The API "
            "Client makes network requests only when you explicitly send a request. "
            "These settings apply only to the API Client. DevKitBox does not collect "
            "telemetry or usage analytics."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        form = QFormLayout()

        self._timeout_spin = QSpinBox()
        self._timeout_spin.setRange(1, 300)
        self._timeout_spin.setSuffix(" s")
        self._timeout_spin.setValue(self.context.settings.request_timeout_seconds)
        self._timeout_spin.valueChanged.connect(self._on_timeout_changed)
        form.addRow("Request timeout", self._timeout_spin)

        self._proxy_edit = QLineEdit(self.context.settings.http_proxy_url)
        self._proxy_edit.setPlaceholderText("http://proxy.example.com:8080 (leave empty for none)")
        self._proxy_edit.editingFinished.connect(self._on_proxy_changed)
        form.addRow("HTTP/HTTPS proxy", self._proxy_edit)

        layout.addLayout(form)

        self._verify_ssl_check = QCheckBox("Verify SSL certificates")
        self._verify_ssl_check.setChecked(self.context.settings.verify_ssl_certificates)
        self._verify_ssl_check.toggled.connect(self._on_verify_ssl_toggled)
        layout.addWidget(self._verify_ssl_check)

        warning = QLabel(
            "⚠ Turning this off disables TLS certificate validation for all API "
            "Client requests — only do this against a trusted server you control "
            "(e.g. one using a self-signed certificate)."
        )
        warning.setWordWrap(True)
        warning.setObjectName("toolDescription")
        layout.addWidget(warning)

        layout.addStretch(1)
        return tab

    def _build_privacy_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)

        intro = QLabel(
            "Both settings below are off by default. DevKitBox never transmits "
            "this data — it stays in your local database and can be cleared "
            "from the History page at any time."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        self._tool_history_check = QCheckBox("Remember tool input/output history")
        self._tool_history_check.setChecked(self.context.settings.tool_history_enabled)
        self._tool_history_check.toggled.connect(self._on_tool_history_toggled)
        layout.addWidget(self._tool_history_check)

        self._clipboard_history_check = QCheckBox("Remember clipboard history")
        self._clipboard_history_check.setChecked(self.context.settings.clipboard_history_enabled)
        self._clipboard_history_check.toggled.connect(self._on_clipboard_history_toggled)
        layout.addWidget(self._clipboard_history_check)

        layout.addStretch(1)
        return tab

    def _build_updates_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)

        layout.addWidget(QLabel(f"Current version: {APP_VERSION}"))

        note = QLabel(
            "DevKitBox never checks for updates in the background — checks "
            "only happen when you press the button below, per the app's "
            "privacy guarantee."
        )
        note.setWordWrap(True)
        note.setObjectName("toolDescription")
        layout.addWidget(note)

        self._check_updates_thread: QThread | None = None
        self._check_updates_worker: _UpdateCheckWorker | None = None

        self._check_updates_button = QPushButton("Check for Updates")
        self._check_updates_button.clicked.connect(self._on_check_for_updates)
        layout.addWidget(self._check_updates_button)

        self._update_status_label = QLabel("")
        self._update_status_label.setWordWrap(True)
        self._update_status_label.setOpenExternalLinks(True)
        layout.addWidget(self._update_status_label)

        layout.addStretch(1)
        return tab

    def _build_about_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(6)

        name = QLabel(APP_DISPLAY_NAME)
        name.setStyleSheet("font-size: 18px; font-weight: 700;")
        layout.addWidget(name)

        layout.addWidget(QLabel(APP_TAGLINE))
        layout.addWidget(QLabel(f"Version {APP_VERSION}"))

        website = QLabel(f'<a href="{WEBSITE_URL}">{WEBSITE_URL}</a>')
        website.setOpenExternalLinks(True)
        layout.addWidget(website)

        if GITHUB_URL:
            github = QLabel(f'<a href="{GITHUB_URL}">{GITHUB_URL}</a>')
            github.setOpenExternalLinks(True)
            layout.addWidget(github)

        made_by = QLabel('Made by <a href="https://ibakas.com">Ioannis Bakas</a>')
        made_by.setOpenExternalLinks(True)
        layout.addWidget(made_by)

        logs_button = QPushButton("Open Logs Folder")
        logs_button.clicked.connect(self._open_logs_folder)
        layout.addWidget(logs_button)

        layout.addStretch(1)
        return tab

    def _on_theme_changed(self, value: str) -> None:
        self.context.settings.theme = value
        self.context.settings_service.set("theme", value)
        self.theme_changed.emit()

    def _on_tool_history_toggled(self, checked: bool) -> None:
        self.context.settings.tool_history_enabled = checked
        self.context.settings_service.set("tool_history_enabled", checked)

    def _on_clipboard_history_toggled(self, checked: bool) -> None:
        self.context.settings.clipboard_history_enabled = checked
        self.context.settings_service.set("clipboard_history_enabled", checked)

    def _on_timeout_changed(self, value: int) -> None:
        self.context.settings.request_timeout_seconds = value
        self.context.settings_service.set("request_timeout_seconds", value)

    def _on_proxy_changed(self) -> None:
        value = self._proxy_edit.text().strip()
        self.context.settings.http_proxy_url = value
        self.context.settings_service.set("http_proxy_url", value)

    def _on_verify_ssl_toggled(self, checked: bool) -> None:
        self.context.settings.verify_ssl_certificates = checked
        self.context.settings_service.set("verify_ssl_certificates", checked)

    def _on_check_for_updates(self) -> None:
        self._check_updates_button.setEnabled(False)
        self._update_status_label.setText("Checking...")

        settings = self.context.settings
        self._check_updates_thread = QThread(self)
        self._check_updates_worker = _UpdateCheckWorker(
            settings.request_timeout_seconds,
            settings.http_proxy_url,
            settings.verify_ssl_certificates,
        )
        self._check_updates_worker.moveToThread(self._check_updates_thread)
        self._check_updates_thread.started.connect(self._check_updates_worker.run)
        self._check_updates_worker.finished.connect(self._on_update_check_finished)
        self._check_updates_worker.failed.connect(self._on_update_check_failed)
        self._check_updates_worker.finished.connect(self._check_updates_thread.quit)
        self._check_updates_worker.failed.connect(self._check_updates_thread.quit)
        self._check_updates_thread.finished.connect(self._check_updates_worker.deleteLater)
        self._check_updates_thread.start()

    def _on_update_check_finished(self, result: UpdateCheckResult) -> None:
        self._check_updates_button.setEnabled(True)
        if result.is_update_available:
            self._update_status_label.setText(
                f"Version {result.latest_version} is available — "
                f'<a href="{result.release_url}">view release</a>'
            )
        else:
            self._update_status_label.setText("You're up to date.")

    def _on_update_check_failed(self, message: str) -> None:
        self._check_updates_button.setEnabled(True)
        self._update_status_label.setText(f"Update check failed: {message}")

    def _on_accent_changed(self, name: str) -> None:
        color = _ACCENT_PRESETS[name]
        self.context.settings.accent_color = color
        self.context.settings_service.set("accent_color", color)
        self.theme_changed.emit()

    def _open_logs_folder(self) -> None:
        log_dir = str(get_log_dir())
        if sys.platform == "win32":
            os.startfile(log_dir)  # noqa: S606
        else:
            subprocess.run(["xdg-open", log_dir], check=False)
