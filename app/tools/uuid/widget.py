"""UUID Generator tool page: v1/v4/v5, bulk generation, formatting options."""

from __future__ import annotations

import uuid

from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
)

from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.uuid.logic import NAMESPACE_PRESETS, format_uuid, generate_bulk
from app.ui.widgets.code_editor import CodeEditor
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="uuid_generator",
    name="UUID Generator",
    description="Generate unique identifiers (v1, v4, v5) in bulk.",
    category="Generators",
    keywords=("uuid", "guid", "generator", "identifier"),
)

_BULK_OPTIONS = [1, 10, 50, 100, 1000]


class UuidGeneratorTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        version_row = QHBoxLayout()
        version_row.addWidget(QLabel("Version"))
        self._version_group = QButtonGroup(self)
        self._v1_radio = QRadioButton("v1")
        self._v4_radio = QRadioButton("v4")
        self._v4_radio.setChecked(True)
        self._v5_radio = QRadioButton("v5")
        for radio in (self._v1_radio, self._v4_radio, self._v5_radio):
            self._version_group.addButton(radio)
            version_row.addWidget(radio)
        self._v5_radio.toggled.connect(self._on_v5_toggled)
        version_row.addStretch(1)
        layout.addLayout(version_row)

        self._v5_row = QHBoxLayout()
        self._v5_row.addWidget(QLabel("Namespace"))
        self._namespace_combo = QComboBox()
        self._namespace_combo.addItems([*NAMESPACE_PRESETS.keys(), "Custom"])
        self._namespace_combo.currentTextChanged.connect(self._on_namespace_changed)
        self._v5_row.addWidget(self._namespace_combo)

        self._custom_namespace_edit = QLineEdit()
        self._custom_namespace_edit.setPlaceholderText("Custom namespace UUID")
        self._custom_namespace_edit.hide()
        self._v5_row.addWidget(self._custom_namespace_edit)

        self._v5_row.addWidget(QLabel("Name"))
        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("example.com")
        self._v5_row.addWidget(self._name_edit)
        self._set_v5_row_visible(False)
        layout.addLayout(self._v5_row)

        options_row = QHBoxLayout()
        options_row.addWidget(QLabel("Count"))
        self._count_combo = QComboBox()
        self._count_combo.addItems([str(n) for n in _BULK_OPTIONS])
        options_row.addWidget(self._count_combo)

        self._uppercase_check = QCheckBox("Uppercase")
        self._braces_check = QCheckBox("Braces")
        self._no_hyphens_check = QCheckBox("No hyphens")
        for check in (self._uppercase_check, self._braces_check, self._no_hyphens_check):
            options_row.addWidget(check)
        options_row.addStretch(1)
        layout.addLayout(options_row)

        layout.addWidget(QLabel("OUTPUT"))
        self._output = CodeEditor(read_only=True)
        layout.addWidget(self._output, stretch=1)

    def build_actions(self, layout: QHBoxLayout) -> None:
        generate_button = QPushButton("Generate")
        generate_button.setObjectName("primaryButton")
        generate_button.clicked.connect(self._generate)
        layout.addWidget(generate_button)
        layout.addStretch(1)

        copy_button = QPushButton("Copy All")
        copy_button.clicked.connect(self._copy_all)
        layout.addWidget(copy_button)

    def _on_v5_toggled(self, checked: bool) -> None:
        self._set_v5_row_visible(checked)

    def _set_v5_row_visible(self, visible: bool) -> None:
        for i in range(self._v5_row.count()):
            widget = self._v5_row.itemAt(i).widget()
            if widget:
                widget.setVisible(visible)
        if visible:
            self._on_namespace_changed(self._namespace_combo.currentText())

    def _on_namespace_changed(self, name: str) -> None:
        self._custom_namespace_edit.setVisible(name == "Custom")

    def _selected_version(self) -> int:
        if self._v1_radio.isChecked():
            return 1
        if self._v5_radio.isChecked():
            return 5
        return 4

    def _generate(self) -> None:
        version = self._selected_version()
        count = int(self._count_combo.currentText())

        namespace = None
        name = ""
        if version == 5:
            name = self._name_edit.text()
            if not name:
                show_toast(self, "Enter a name for v5 UUIDs", "warning")
                return
            namespace_choice = self._namespace_combo.currentText()
            if namespace_choice == "Custom":
                try:
                    namespace = uuid.UUID(self._custom_namespace_edit.text().strip())
                except ValueError:
                    show_toast(self, "Invalid custom namespace UUID", "error")
                    return
            else:
                namespace = NAMESPACE_PRESETS[namespace_choice]

        values = generate_bulk(version, count, namespace, name)
        formatted = [
            format_uuid(
                v,
                uppercase=self._uppercase_check.isChecked(),
                braces=self._braces_check.isChecked(),
                hyphens=not self._no_hyphens_check.isChecked(),
            )
            for v in values
        ]
        self._output.setPlainText("\n".join(formatted))
        show_toast(self, f"Generated {count} UUID{'s' if count != 1 else ''}", "success")

    def _copy_all(self) -> None:
        text = self._output.toPlainText()
        if not text:
            show_toast(self, "Nothing to copy", "warning")
            return
        self.copy_to_clipboard(text)
        show_toast(self, "Copied to clipboard", "success")
