"""Hash Generator tool page: text and file hashing with a threaded file worker."""

from __future__ import annotations

from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from app.core.exceptions import FileOperationError
from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.hash.logic import ALGORITHMS, hash_file, hash_text
from app.ui.widgets.code_editor import CodeEditor
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="hash_generator",
    name="Hash Generator",
    description="Generate cryptographic hashes locally, for text or files.",
    category="Encoding",
    keywords=("hash", "md5", "sha1", "sha256", "sha512", "checksum", "digest"),
)


class _HashFileWorker(QObject):
    progress = Signal(int)
    finished = Signal(dict)
    failed = Signal(str)

    def __init__(self, path: str, algorithms: list[str]) -> None:
        super().__init__()
        self._path = path
        self._algorithms = algorithms

    def run(self) -> None:
        try:
            result = hash_file(self._path, self._algorithms, progress_cb=self._on_progress)
        except FileOperationError as exc:
            self.failed.emit(exc.message)
            return
        self.finished.emit(result)

    def _on_progress(self, done: int, total: int) -> None:
        percent = int(done * 100 / total) if total else 100
        self.progress.emit(percent)


class HashGeneratorTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        self._thread: QThread | None = None
        self._worker: _HashFileWorker | None = None

        algo_row = QHBoxLayout()
        algo_row.addWidget(QLabel("Algorithms"))
        self._algo_checks: dict[str, QCheckBox] = {}
        for name in ALGORITHMS:
            check = QCheckBox(name)
            check.setChecked(name in ("SHA-256", "MD5"))
            algo_row.addWidget(check)
            self._algo_checks[name] = check
        algo_row.addStretch(1)
        layout.addLayout(algo_row)

        layout.addWidget(QLabel("Text input"))
        self._input = CodeEditor(placeholder="Text to hash...")
        self._input.setMaximumHeight(100)
        layout.addWidget(self._input)

        self._progress_bar = QProgressBar()
        self._progress_bar.setVisible(False)
        layout.addWidget(self._progress_bar)

        self._table = QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(["Algorithm", "Hash"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self._table, stretch=1)

    def build_actions(self, layout: QHBoxLayout) -> None:
        hash_text_button = QPushButton("Hash Text")
        hash_text_button.setObjectName("primaryButton")
        hash_text_button.clicked.connect(self._hash_text)
        layout.addWidget(hash_text_button)

        hash_file_button = QPushButton("Hash File...")
        hash_file_button.clicked.connect(self._hash_file)
        layout.addWidget(hash_file_button)
        layout.addStretch(1)

        copy_all_button = QPushButton("Copy All")
        copy_all_button.clicked.connect(self._copy_all)
        layout.addWidget(copy_all_button)

    def _selected_algorithms(self) -> list[str]:
        return [name for name, check in self._algo_checks.items() if check.isChecked()]

    def _hash_text(self) -> None:
        algorithms = self._selected_algorithms()
        if not algorithms:
            show_toast(self, "Select at least one algorithm", "warning")
            return
        results = hash_text(self._input.toPlainText(), algorithms)
        self._populate_table(results)
        show_toast(self, "Hashed", "success")

    def _hash_file(self) -> None:
        algorithms = self._selected_algorithms()
        if not algorithms:
            show_toast(self, "Select at least one algorithm", "warning")
            return
        path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if not path:
            return

        self._table.setRowCount(0)
        self._progress_bar.setValue(0)
        self._progress_bar.setVisible(True)

        self._thread = QThread(self)
        self._worker = _HashFileWorker(path, algorithms)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._progress_bar.setValue)
        self._worker.finished.connect(self._on_file_hashed)
        self._worker.failed.connect(self._on_file_hash_failed)
        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._thread.finished.connect(self._worker.deleteLater)
        self._thread.start()

    def _on_file_hashed(self, results: dict) -> None:
        self._progress_bar.setVisible(False)
        self._populate_table(results)
        show_toast(self, "File hashed", "success")

    def _on_file_hash_failed(self, message: str) -> None:
        self._progress_bar.setVisible(False)
        show_toast(self, message, "error")

    def _populate_table(self, results: dict[str, str]) -> None:
        self._table.setRowCount(len(results))
        for row, (name, digest) in enumerate(results.items()):
            self._table.setItem(row, 0, QTableWidgetItem(name))
            self._table.setItem(row, 1, QTableWidgetItem(digest))

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
