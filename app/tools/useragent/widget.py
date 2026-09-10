"""User-Agent Parser tool page."""

from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from app.core.exceptions import ValidationError
from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.useragent.logic import parse_user_agent
from app.ui.widgets.code_editor import CodeEditor
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="user_agent_parser",
    name="User-Agent Parser",
    description="Parse a User-Agent string into browser, OS, and device details.",
    category="Network",
    keywords=("user agent", "useragent", "ua", "browser", "parse", "device"),
)


class UserAgentParserTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        layout.addWidget(QLabel("User-Agent string"))
        self._input = CodeEditor(
            placeholder="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ..."
        )
        self._input.setMaximumHeight(80)
        self._input.textChanged.connect(self._refresh)
        layout.addWidget(self._input)

        form = QFormLayout()
        self._labels: dict[str, QLabel] = {}
        for field in ("Browser", "Operating System", "Device Type", "Bot / Crawler"):
            label = QLabel("—")
            form.addRow(field, label)
            self._labels[field] = label
        layout.addLayout(form)

        layout.addStretch(1)

    def build_actions(self, layout: QHBoxLayout) -> None:
        copy_button = QPushButton("Copy Summary")
        copy_button.setObjectName("primaryButton")
        copy_button.clicked.connect(self._copy_summary)
        layout.addWidget(copy_button)
        layout.addStretch(1)

    def _refresh(self) -> None:
        try:
            info = parse_user_agent(self._input.toPlainText())
        except ValidationError:
            for label in self._labels.values():
                label.setText("—")
            return

        browser = f"{info.browser} {info.browser_version}" if info.browser else "Unknown"
        os_text = f"{info.os} {info.os_version}" if info.os else "Unknown"

        self._labels["Browser"].setText(browser)
        self._labels["Operating System"].setText(os_text)
        self._labels["Device Type"].setText(info.device_type)
        self._labels["Bot / Crawler"].setText("Yes" if info.is_bot else "No")

    def _copy_summary(self) -> None:
        parts = [f"{name}: {label.text()}" for name, label in self._labels.items()]
        text = "\n".join(parts)
        if not any(label.text() != "—" for label in self._labels.values()):
            show_toast(self, "Nothing to copy", "warning")
            return
        self.copy_to_clipboard(text)
        show_toast(self, "Copied to clipboard", "success")
