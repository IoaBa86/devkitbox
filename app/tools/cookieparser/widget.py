"""Cookie Parser tool page: parse a Set-Cookie or Cookie header."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QButtonGroup,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.core.exceptions import ValidationError
from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.cookieparser.logic import parse_cookie_header, parse_set_cookie
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="cookie_parser",
    name="Cookie Parser",
    description="Parse a Set-Cookie response header or a Cookie request header.",
    category="Network",
    keywords=("cookie", "set-cookie", "http", "header", "parser"),
)

_FIELDS = (
    "Name",
    "Value",
    "Domain",
    "Path",
    "Expires",
    "Max-Age",
    "SameSite",
    "Secure",
    "HttpOnly",
)


class CookieParserTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Header type"))
        self._mode_group = QButtonGroup(self)
        self._set_cookie_radio = QRadioButton("Set-Cookie (response)")
        self._set_cookie_radio.setChecked(True)
        self._set_cookie_radio.toggled.connect(self._on_mode_toggled)
        self._cookie_radio = QRadioButton("Cookie (request)")
        for radio in (self._set_cookie_radio, self._cookie_radio):
            self._mode_group.addButton(radio)
            mode_row.addWidget(radio)
        mode_row.addStretch(1)
        layout.addLayout(mode_row)

        self._input = QLineEdit()
        self._input.setPlaceholderText(
            "session_id=abc123; Domain=example.com; Path=/; Secure; HttpOnly; SameSite=Lax"
        )
        layout.addWidget(self._input)

        self._form_widget = QWidget()
        form = QFormLayout(self._form_widget)
        self._labels: dict[str, QLabel] = {}
        for name in _FIELDS:
            label = QLabel("—")
            form.addRow(name, label)
            self._labels[name] = label
        layout.addWidget(self._form_widget)

        self._table = QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(["Name", "Value"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.hide()
        layout.addWidget(self._table, stretch=1)

        layout.addStretch(1)

    def build_actions(self, layout: QHBoxLayout) -> None:
        parse_button = QPushButton("Parse")
        parse_button.setObjectName("primaryButton")
        parse_button.clicked.connect(self._parse)
        layout.addWidget(parse_button)
        layout.addStretch(1)

    def _on_mode_toggled(self, is_set_cookie: bool) -> None:
        self._form_widget.setVisible(is_set_cookie)
        self._table.setVisible(not is_set_cookie)

    def _parse(self) -> None:
        if self._set_cookie_radio.isChecked():
            self._parse_set_cookie()
        else:
            self._parse_cookie_header()

    def _parse_set_cookie(self) -> None:
        self._table.hide()
        self._form_widget.show()
        try:
            info = parse_set_cookie(self._input.text())
        except ValidationError as exc:
            show_toast(self, exc.message, "error")
            for label in self._labels.values():
                label.setText("—")
            return

        self._labels["Name"].setText(info.name)
        self._labels["Value"].setText(info.value)
        self._labels["Domain"].setText(info.domain or "—")
        self._labels["Path"].setText(info.path or "—")
        self._labels["Expires"].setText(info.expires or "—")
        self._labels["Max-Age"].setText(info.max_age or "—")
        self._labels["SameSite"].setText(info.same_site or "—")
        self._labels["Secure"].setText("Yes" if info.secure else "No")
        self._labels["HttpOnly"].setText("Yes" if info.http_only else "No")
        show_toast(self, "Cookie parsed", "success")

    def _parse_cookie_header(self) -> None:
        self._form_widget.hide()
        self._table.show()
        pairs = parse_cookie_header(self._input.text())
        self._table.setRowCount(len(pairs))
        for row, (name, value) in enumerate(pairs.items()):
            self._table.setItem(row, 0, QTableWidgetItem(name))
            self._table.setItem(row, 1, QTableWidgetItem(value))
        if not pairs:
            show_toast(self, "No cookies found", "warning")
        else:
            show_toast(self, f"Parsed {len(pairs)} cookies", "success")
