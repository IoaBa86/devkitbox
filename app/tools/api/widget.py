"""API Client tool page: send HTTP requests and inspect the response.

A network request is made only when the user presses Send, per the app's
privacy guarantee (see README > Privacy).
"""

from __future__ import annotations

from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from app.core.exceptions import NetworkError, ValidationError
from app.models.tool import ToolMetadata
from app.tools.api.logic import (
    METHODS,
    ApiRequest,
    ApiResponse,
    build_request,
    format_response_body,
    parse_headers_text,
)
from app.tools.base import ToolWidget
from app.ui.widgets.code_editor import CodeEditor
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="api_client",
    name="API Client",
    description="Send HTTP requests and inspect responses. Network use is opt-in per request.",
    category="Network",
    keywords=("api", "http", "rest", "request", "client", "postman"),
)


class _RequestWorker(QObject):
    finished = Signal(object)
    failed = Signal(str)

    def __init__(
        self, request: ApiRequest, timeout: float, proxy_url: str, verify_ssl: bool
    ) -> None:
        super().__init__()
        self._request = request
        self._timeout = timeout
        self._proxy_url = proxy_url
        self._verify_ssl = verify_ssl

    def run(self) -> None:
        from app.tools.api.logic import send_request

        try:
            response = send_request(self._request, self._timeout, self._proxy_url, self._verify_ssl)
        except NetworkError as exc:
            self.failed.emit(exc.message)
            return
        self.finished.emit(response)


class ApiClientTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        self._thread: QThread | None = None
        self._worker: _RequestWorker | None = None

        request_row = QHBoxLayout()
        self._method_combo = QComboBox()
        self._method_combo.addItems(METHODS)
        request_row.addWidget(self._method_combo)

        self._url_edit = QLineEdit()
        self._url_edit.setPlaceholderText("https://api.example.com/resource")
        request_row.addWidget(self._url_edit, stretch=1)
        layout.addLayout(request_row)

        layout.addWidget(QLabel("HEADERS (one per line, Key: Value)"))
        self._headers_input = CodeEditor(placeholder="Content-Type: application/json")
        self._headers_input.setMaximumHeight(80)
        layout.addWidget(self._headers_input)

        layout.addWidget(QLabel("BODY"))
        self._body_input = CodeEditor(placeholder="Request body (for POST/PUT/PATCH)...")
        self._body_input.setMaximumHeight(120)
        layout.addWidget(self._body_input)

        self._status_label = QLabel("")
        layout.addWidget(self._status_label)

        layout.addWidget(QLabel("RESPONSE"))
        self._response_output = CodeEditor(read_only=True)
        layout.addWidget(self._response_output, stretch=1)

    def build_actions(self, layout: QHBoxLayout) -> None:
        self._send_button = QPushButton("Send")
        self._send_button.setObjectName("primaryButton")
        self._send_button.clicked.connect(self._send)
        layout.addWidget(self._send_button)
        layout.addStretch(1)

        copy_button = QPushButton("Copy Response")
        copy_button.clicked.connect(self._copy_response)
        layout.addWidget(copy_button)

    def _send(self) -> None:
        try:
            headers = parse_headers_text(self._headers_input.toPlainText())
            request = build_request(
                self._method_combo.currentText(),
                self._url_edit.text(),
                headers,
                self._body_input.toPlainText(),
            )
        except ValidationError as exc:
            show_toast(self, exc.message, "error")
            return

        self._send_button.setEnabled(False)
        self._status_label.setText("Sending...")

        settings = self.context.settings
        self._thread = QThread(self)
        self._worker = _RequestWorker(
            request,
            settings.request_timeout_seconds,
            settings.http_proxy_url,
            settings.verify_ssl_certificates,
        )
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_response)
        self._worker.failed.connect(self._on_failed)
        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._thread.finished.connect(self._worker.deleteLater)
        self._thread.start()

    def _on_response(self, response: ApiResponse) -> None:
        self._send_button.setEnabled(True)
        self._status_label.setText(
            f"{response.status_code} {response.reason}  |  {response.elapsed_ms:.0f} ms"
        )
        self._response_output.setPlainText(format_response_body(response))
        show_toast(self, "Request complete", "success")

    def _on_failed(self, message: str) -> None:
        self._send_button.setEnabled(True)
        self._status_label.setText("Failed")
        show_toast(self, message, "error")

    def _copy_response(self) -> None:
        text = self._response_output.toPlainText()
        if not text:
            show_toast(self, "Nothing to copy", "warning")
            return
        self.copy_to_clipboard(text)
        show_toast(self, "Copied to clipboard", "success")
