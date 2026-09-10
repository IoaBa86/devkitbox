"""File Information tool page: inspect size, MIME type, timestamps, and hashes."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from app.core.exceptions import FileOperationError
from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.fileinfo.logic import FileInfo, format_size, inspect_file
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="file_information",
    name="File Information",
    description="Inspect size, MIME type, timestamps, and hashes for any local file.",
    category="Files",
    keywords=("file", "info", "mime", "size", "hash", "metadata"),
)


class FileInformationTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        self._path_label = QLabel("No file selected")
        self._path_label.setWordWrap(True)
        layout.addWidget(self._path_label)

        self._table = QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(["Property", "Value"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self._table, stretch=1)

        self._info: FileInfo | None = None

    def build_actions(self, layout: QHBoxLayout) -> None:
        select_button = QPushButton("Select File...")
        select_button.setObjectName("primaryButton")
        select_button.clicked.connect(self._select_file)
        layout.addWidget(select_button)
        layout.addStretch(1)

        copy_button = QPushButton("Copy All")
        copy_button.clicked.connect(self._copy_all)
        layout.addWidget(copy_button)

    def _select_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if not path:
            return
        try:
            info = inspect_file(path)
        except FileOperationError as exc:
            show_toast(self, exc.message, "error")
            return

        self._info = info
        self._path_label.setText(info.path)
        rows = [
            ("Name", info.name),
            ("Size", f"{format_size(info.size_bytes)} ({info.size_bytes:,} bytes)"),
            ("MIME Type", info.mime_type),
            ("Extension", info.extension or "(none)"),
            ("Created", info.created.isoformat()),
            ("Modified", info.modified.isoformat()),
            ("MD5", info.md5),
            ("SHA-256", info.sha256),
        ]
        self._table.setRowCount(len(rows))
        for row, (label, value) in enumerate(rows):
            self._table.setItem(row, 0, QTableWidgetItem(label))
            self._table.setItem(row, 1, QTableWidgetItem(value))
        show_toast(self, "File inspected", "success")

    def _copy_all(self) -> None:
        if self._table.rowCount() == 0:
            show_toast(self, "Nothing to copy", "warning")
            return
        lines = [
            f"{self._table.item(row, 0).text()}: {self._table.item(row, 1).text()}"
            for row in range(self._table.rowCount())
        ]
        self.copy_to_clipboard("\n".join(lines))
        show_toast(self, "Copied to clipboard", "success")
