"""Unit Converter tool page: data size and time duration conversion."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from app.core.exceptions import ValidationError
from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.unitconvert.logic import UNIT_FAMILIES, convert_to_all

METADATA = ToolMetadata(
    id="unit_converter",
    name="Unit Converter",
    description="Convert data size (KB/MB/GB, decimal and binary) and time durations.",
    category="Development",
    keywords=("unit", "convert", "bytes", "kilobytes", "size", "time", "duration"),
)


class UnitConverterTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("Family"))
        self._family_combo = QComboBox()
        self._family_combo.addItems(list(UNIT_FAMILIES.keys()))
        self._family_combo.currentTextChanged.connect(self._on_family_changed)
        input_row.addWidget(self._family_combo)

        self._value_spin = QDoubleSpinBox()
        self._value_spin.setRange(0, 1e15)
        self._value_spin.setDecimals(4)
        self._value_spin.setValue(1)
        self._value_spin.valueChanged.connect(self._refresh)
        input_row.addWidget(self._value_spin)

        input_row.addWidget(QLabel("as"))
        self._from_combo = QComboBox()
        self._from_combo.currentTextChanged.connect(self._refresh)
        input_row.addWidget(self._from_combo)
        input_row.addStretch(1)
        layout.addLayout(input_row)

        self._table = QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(["Unit", "Value"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self._table, stretch=1)

        self._on_family_changed(self._family_combo.currentText())

    def build_actions(self, layout: QHBoxLayout) -> None:
        pass

    def _on_family_changed(self, family: str) -> None:
        units = list(UNIT_FAMILIES[family].keys())
        self._from_combo.blockSignals(True)
        self._from_combo.clear()
        self._from_combo.addItems(units)
        self._from_combo.blockSignals(False)
        self._refresh()

    def _refresh(self) -> None:
        family = self._family_combo.currentText()
        from_unit = self._from_combo.currentText()
        if not from_unit:
            return

        try:
            results = convert_to_all(self._value_spin.value(), from_unit, family)
        except ValidationError:
            self._table.setRowCount(0)
            return

        self._table.setRowCount(len(results))
        for row, (unit, value) in enumerate(results.items()):
            self._table.setItem(row, 0, QTableWidgetItem(unit))
            self._table.setItem(row, 1, QTableWidgetItem(f"{value:,.4f}".rstrip("0").rstrip(".")))
