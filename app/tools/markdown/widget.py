"""Markdown Preview tool page: live-rendered Markdown with a table of contents."""

from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QTextBrowser, QVBoxLayout

from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.markdown.logic import build_toc, extract_headings, word_count
from app.ui.widgets.code_editor import CodeEditor
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="markdown_preview",
    name="Markdown Preview",
    description="Live-render Markdown with a generated table of contents.",
    category="Text",
    keywords=("markdown", "md", "preview", "render", "toc"),
)


class MarkdownPreviewTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        panes = QHBoxLayout()
        panes.setSpacing(12)

        input_col = QVBoxLayout()
        input_col.addWidget(QLabel("MARKDOWN"))
        self._input = CodeEditor(placeholder="# Heading\n\nWrite Markdown here...")
        self._input.textChanged.connect(self._render)
        input_col.addWidget(self._input)
        panes.addLayout(input_col)

        preview_col = QVBoxLayout()
        preview_col.addWidget(QLabel("PREVIEW"))
        self._preview = QTextBrowser()
        self._preview.setOpenExternalLinks(True)
        preview_col.addWidget(self._preview)
        panes.addLayout(preview_col)

        layout.addLayout(panes, stretch=1)

        self._stats_label = QLabel("")
        layout.addWidget(self._stats_label)

    def build_actions(self, layout: QHBoxLayout) -> None:
        toc_button = QPushButton("Insert Table of Contents")
        toc_button.clicked.connect(self._insert_toc)
        layout.addWidget(toc_button)
        layout.addStretch(1)

        copy_html_button = QPushButton("Copy HTML")
        copy_html_button.clicked.connect(self._copy_html)
        layout.addWidget(copy_html_button)

    def _render(self) -> None:
        text = self._input.toPlainText()
        self._preview.setMarkdown(text)
        headings = extract_headings(text)
        self._stats_label.setText(f"{word_count(text)} words  |  {len(headings)} headings")

    def _insert_toc(self) -> None:
        text = self._input.toPlainText()
        headings = extract_headings(text)
        if not headings:
            show_toast(self, "No headings found", "warning")
            return
        toc = build_toc(headings)
        self._input.setPlainText(f"{toc}\n\n{text}")
        show_toast(self, "Table of contents inserted", "success")

    def _copy_html(self) -> None:
        html = self._preview.toHtml()
        if not html:
            show_toast(self, "Nothing to copy", "warning")
            return
        self.copy_to_clipboard(html)
        show_toast(self, "Copied HTML to clipboard", "success")
