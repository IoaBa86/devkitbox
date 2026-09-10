"""Timezone Converter tool page: convert a time across common zones at once."""

from __future__ import annotations

from PySide6.QtCore import QDateTime
from PySide6.QtWidgets import (
    QComboBox,
    QDateTimeEdit,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from app.core.exceptions import ValidationError
from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.timezone.logic import COMMON_ZONES, convert_to_zones
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="timezone_converter",
    name="Timezone Converter",
    description="Convert a date/time across common timezones side-by-side.",
    category="Development",
    keywords=("timezone", "time zone", "convert", "utc", "world clock"),
)


class TimezoneConverterTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("Source zone"))
        self._source_zone_combo = QComboBox()
        self._source_zone_combo.addItems(list(COMMON_ZONES))
        self._source_zone_combo.currentTextChanged.connect(self._refresh)
        input_row.addWidget(self._source_zone_combo)

        self._datetime_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self._datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
        self._datetime_edit.setCalendarPopup(True)
        self._datetime_edit.dateTimeChanged.connect(self._refresh)
        input_row.addWidget(self._datetime_edit)

        now_button = QPushButton("Now")
        now_button.clicked.connect(self._set_now)
        input_row.addWidget(now_button)
        input_row.addStretch(1)
        layout.addLayout(input_row)

        self._table = QTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(["Zone", "Local Time", "UTC Offset"])
        self._table.setColumnWidth(0, 160)
        self._table.setColumnWidth(1, 220)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self._table, stretch=1)

        self._refresh()

    def build_actions(self, layout: QHBoxLayout) -> None:
        pass

    def _set_now(self) -> None:
        self._datetime_edit.setDateTime(QDateTime.currentDateTime())

    def _refresh(self) -> None:
        qt_dt = self._datetime_edit.dateTime()
        source_dt = qt_dt.toPython()
        source_zone = self._source_zone_combo.currentText()

        try:
            results = convert_to_zones(source_dt, source_zone, list(COMMON_ZONES))
        except ValidationError as exc:
            show_toast(self, exc.message, "error")
            return

        self._table.setRowCount(len(results))
        for row, result in enumerate(results):
            self._table.setItem(row, 0, QTableWidgetItem(result.zone_name))
            self._table.setItem(
                row, 1, QTableWidgetItem(result.local_time.strftime("%Y-%m-%d %H:%M %Z"))
            )
            self._table.setItem(row, 2, QTableWidgetItem(result.utc_offset))
