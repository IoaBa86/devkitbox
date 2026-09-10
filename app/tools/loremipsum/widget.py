"""Lorem Ipsum Generator tool page."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from app.core.exceptions import ValidationError
from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.loremipsum.logic import UNITS, generate
from app.ui.widgets.code_editor import CodeEditor
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="lorem_ipsum_generator",
    name="Lorem Ipsum Generator",
    description="Generate placeholder text by words, sentences, or paragraphs.",
    category="Generators",
    keywords=("lorem", "ipsum", "placeholder", "text", "generator", "filler"),
)


class LoremIpsumGeneratorTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        options_row = QHBoxLayout()
        options_row.addWidget(QLabel("Count"))
        self._count_spin = QSpinBox()
        self._count_spin.setRange(1, 500)
        self._count_spin.setValue(3)
        options_row.addWidget(self._count_spin)

        self._unit_combo = QComboBox()
        self._unit_combo.addItems(list(UNITS))
        self._unit_combo.setCurrentText("Paragraphs")
        options_row.addWidget(self._unit_combo)

        self._start_lorem_check = QCheckBox("Start with 'Lorem ipsum dolor sit amet'")
        self._start_lorem_check.setChecked(True)
        options_row.addWidget(self._start_lorem_check)
        options_row.addStretch(1)
        layout.addLayout(options_row)

        layout.addWidget(QLabel("OUTPUT"))
        self._output = CodeEditor(read_only=True)
        layout.addWidget(self._output, stretch=1)

        self._generate()

    def build_actions(self, layout: QHBoxLayout) -> None:
        generate_button = QPushButton("Generate")
        generate_button.setObjectName("primaryButton")
        generate_button.clicked.connect(self._generate)
        layout.addWidget(generate_button)
        layout.addStretch(1)

        copy_button = QPushButton("Copy")
        copy_button.clicked.connect(self._copy_output)
        layout.addWidget(copy_button)

    def _generate(self) -> None:
        try:
            text = generate(
                self._count_spin.value(),
                self._unit_combo.currentText(),
                self._start_lorem_check.isChecked(),
            )
        except ValidationError as exc:
            show_toast(self, exc.message, "error")
            return
        self._output.setPlainText(text)
        show_toast(self, "Generated", "success")

    def _copy_output(self) -> None:
        text = self._output.toPlainText()
        if not text:
            show_toast(self, "Nothing to copy", "warning")
            return
        self.copy_to_clipboard(text)
        show_toast(self, "Copied to clipboard", "success")
