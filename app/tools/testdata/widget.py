"""Random Test Data tool page: generate mock records as JSON or CSV."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QTableWidget,
    QVBoxLayout,
)

from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.testdata.logic import FIELD_GENERATORS, FieldSpec, generate_records, to_csv, to_json
from app.ui.widgets.code_editor import CodeEditor
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="random_test_data",
    name="Random Test Data",
    description="Generate mock records (names, emails, dates, and more) as JSON or CSV.",
    category="Generators",
    keywords=("test data", "mock", "fake", "generator", "sample data", "fixtures"),
)


class RandomTestDataTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        self._field_table = QTableWidget(0, 2)
        self._field_table.setHorizontalHeaderLabels(["Field Name", "Type"])
        self._field_table.horizontalHeader().setStretchLastSection(True)
        self._field_table.verticalHeader().setVisible(False)
        self._field_table.verticalHeader().setDefaultSectionSize(36)
        layout.addWidget(self._field_table)

        field_actions = QHBoxLayout()
        add_field_button = QPushButton("Add Field")
        add_field_button.clicked.connect(self._add_field)
        field_actions.addWidget(add_field_button)

        remove_field_button = QPushButton("Remove Selected")
        remove_field_button.clicked.connect(self._remove_field)
        field_actions.addWidget(remove_field_button)
        field_actions.addStretch(1)
        layout.addLayout(field_actions)

        options_row = QHBoxLayout()
        options_row.addWidget(QLabel("Count"))
        self._count_spin = QSpinBox()
        self._count_spin.setRange(1, 10000)
        self._count_spin.setValue(10)
        options_row.addWidget(self._count_spin)

        options_row.addWidget(QLabel("Format"))
        self._format_group = QButtonGroup(self)
        self._json_radio = QRadioButton("JSON")
        self._json_radio.setChecked(True)
        self._csv_radio = QRadioButton("CSV")
        for radio in (self._json_radio, self._csv_radio):
            self._format_group.addButton(radio)
            options_row.addWidget(radio)
        options_row.addStretch(1)
        layout.addLayout(options_row)

        layout.addWidget(QLabel("OUTPUT"))
        self._output = CodeEditor(read_only=True)
        layout.addWidget(self._output, stretch=1)

        self._add_field("id", "UUID")
        self._add_field("name", "Full Name")
        self._add_field("email", "Email")

    def build_actions(self, layout: QHBoxLayout) -> None:
        generate_button = QPushButton("Generate")
        generate_button.setObjectName("primaryButton")
        generate_button.clicked.connect(self._generate)
        layout.addWidget(generate_button)
        layout.addStretch(1)

        copy_button = QPushButton("Copy")
        copy_button.clicked.connect(self._copy_output)
        layout.addWidget(copy_button)

    def _add_field(self, name: str = "", field_type: str = "Full Name") -> None:
        row = self._field_table.rowCount()
        self._field_table.insertRow(row)

        name_edit = QLineEdit(name or f"field_{row + 1}")
        self._field_table.setCellWidget(row, 0, name_edit)

        type_combo = QComboBox()
        type_combo.addItems(list(FIELD_GENERATORS.keys()))
        type_combo.setCurrentText(field_type)
        self._field_table.setCellWidget(row, 1, type_combo)

        self._field_table.resizeRowToContents(row)

    def _remove_field(self) -> None:
        row = self._field_table.currentRow()
        if row < 0:
            show_toast(self, "Select a field row to remove", "warning")
            return
        self._field_table.removeRow(row)

    def _collect_fields(self) -> list[FieldSpec]:
        fields = []
        for row in range(self._field_table.rowCount()):
            name_widget = self._field_table.cellWidget(row, 0)
            type_widget = self._field_table.cellWidget(row, 1)
            name = name_widget.text().strip() if isinstance(name_widget, QLineEdit) else ""
            field_type = type_widget.currentText() if isinstance(type_widget, QComboBox) else ""
            if name:
                fields.append(FieldSpec(name=name, field_type=field_type))
        return fields

    def _generate(self) -> None:
        fields = self._collect_fields()
        if not fields:
            show_toast(self, "Add at least one field", "warning")
            return

        records = generate_records(fields, self._count_spin.value())
        if self._json_radio.isChecked():
            self._output.setPlainText(to_json(records))
        else:
            self._output.setPlainText(to_csv(records, [f.name for f in fields]))
        show_toast(self, f"Generated {len(records)} records", "success")

    def _copy_output(self) -> None:
        text = self._output.toPlainText()
        if not text:
            show_toast(self, "Nothing to copy", "warning")
            return
        self.copy_to_clipboard(text)
        show_toast(self, "Copied to clipboard", "success")
