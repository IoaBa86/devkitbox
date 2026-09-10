"""Regex Tester tool page: pattern testing with match highlighting.

Matching uses the ``regex`` package's real timeout (see logic.py) so a
catastrophic-backtracking pattern can't freeze the app.
"""

from __future__ import annotations

from PySide6.QtGui import QColor, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
)

from app.core.exceptions import ValidationError
from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.regex.logic import find_matches
from app.ui.widgets.code_editor import CodeEditor

METADATA = ToolMetadata(
    id="regex_tester",
    name="Regex Tester",
    description="Test regular expressions against sample text with live match highlighting.",
    category="Development",
    keywords=("regex", "regular expression", "pattern", "match", "test"),
)

_HIGHLIGHT_BG = QColor("#F5D90A")
_HIGHLIGHT_FG = QColor("#14161A")


class RegexTesterTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        pattern_row = QHBoxLayout()
        pattern_row.addWidget(QLabel("Pattern"))
        self._pattern_edit = QLineEdit()
        self._pattern_edit.setPlaceholderText(r"\d+")
        self._pattern_edit.textChanged.connect(self._run)
        pattern_row.addWidget(self._pattern_edit, stretch=1)
        layout.addLayout(pattern_row)

        flags_row = QHBoxLayout()
        flags_row.addWidget(QLabel("Flags"))
        self._flag_checks: dict[str, QCheckBox] = {}
        for name, label in (
            ("IGNORECASE", "i"),
            ("MULTILINE", "m"),
            ("DOTALL", "s"),
            ("VERBOSE", "x"),
        ):
            check = QCheckBox(label)
            check.toggled.connect(self._run)
            flags_row.addWidget(check)
            self._flag_checks[name] = check
        flags_row.addStretch(1)
        layout.addLayout(flags_row)

        layout.addWidget(QLabel("Test text"))
        self._text_edit = CodeEditor(placeholder="Text to search...")
        self._text_edit.textChanged.connect(self._run)
        layout.addWidget(self._text_edit)

        self._status_label = QLabel("0 matches")
        self._status_label.setObjectName("toolDescription")
        layout.addWidget(self._status_label)

        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["#", "Match", "Span", "Groups"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self._table, stretch=1)

    def _selected_flags(self) -> list[str]:
        return [name for name, check in self._flag_checks.items() if check.isChecked()]

    def _run(self) -> None:
        pattern = self._pattern_edit.text()
        text = self._text_edit.toPlainText()

        if not pattern:
            self._status_label.setText("0 matches")
            self._table.setRowCount(0)
            self._text_edit.setExtraSelections([])
            return

        try:
            result = find_matches(pattern, text, self._selected_flags())
        except ValidationError as exc:
            self._status_label.setText(exc.message)
            self._table.setRowCount(0)
            self._text_edit.setExtraSelections([])
            return

        self._status_label.setText(
            f"{len(result.matches)} match{'es' if len(result.matches) != 1 else ''}, "
            f"{result.group_count} capture group{'s' if result.group_count != 1 else ''}"
        )

        self._table.setRowCount(len(result.matches))
        for row, match in enumerate(result.matches):
            self._table.setItem(row, 0, QTableWidgetItem(str(match.index)))
            self._table.setItem(row, 1, QTableWidgetItem(match.text))
            self._table.setItem(row, 2, QTableWidgetItem(f"{match.start}-{match.end}"))
            groups_text = ", ".join(g if g is not None else "—" for g in match.groups)
            self._table.setItem(row, 3, QTableWidgetItem(groups_text))

        self._highlight_matches(result.matches)

    def _highlight_matches(self, matches) -> None:
        fmt = QTextCharFormat()
        fmt.setBackground(_HIGHLIGHT_BG)
        fmt.setForeground(_HIGHLIGHT_FG)

        selections = []
        for match in matches:
            cursor = QTextCursor(self._text_edit.document())
            cursor.setPosition(match.start)
            cursor.setPosition(match.end, QTextCursor.MoveMode.KeepAnchor)
            selection = QTextEdit.ExtraSelection()
            selection.cursor = cursor
            selection.format = fmt
            selections.append(selection)
        self._text_edit.setExtraSelections(selections)
