"""Password Generator tool page: random passwords and diceware-style passphrases."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
)

from app.models.tool import ToolMetadata
from app.tools.base import ToolWidget
from app.tools.password.logic import (
    DIGITS,
    LOWERCASE,
    SYMBOLS,
    UPPERCASE,
    PasswordOptions,
    generate_passphrase,
    generate_password,
    password_entropy_bits,
    strength_label,
)
from app.ui.widgets.toast import show_toast

METADATA = ToolMetadata(
    id="password_generator",
    name="Password Generator",
    description="Generate strong random passwords or memorable passphrases, locally.",
    category="Generators",
    keywords=("password", "passphrase", "generator", "secure", "random"),
)


class PasswordGeneratorTool(ToolWidget):
    metadata = METADATA

    def build_content(self, layout: QVBoxLayout) -> None:
        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Mode"))
        self._mode_group = QButtonGroup(self)
        self._password_radio = QRadioButton("Password")
        self._password_radio.setChecked(True)
        self._passphrase_radio = QRadioButton("Passphrase")
        for radio in (self._password_radio, self._passphrase_radio):
            self._mode_group.addButton(radio)
            mode_row.addWidget(radio)
        self._password_radio.toggled.connect(self._on_mode_toggled)
        mode_row.addStretch(1)
        layout.addLayout(mode_row)

        self._password_row = QHBoxLayout()
        self._password_row.addWidget(QLabel("Length"))
        self._length_slider = QSlider(Qt.Orientation.Horizontal)
        self._length_slider.setRange(4, 128)
        self._length_slider.setValue(16)
        self._password_row.addWidget(self._length_slider, stretch=1)
        self._length_spin = QSpinBox()
        self._length_spin.setRange(4, 128)
        self._length_spin.setValue(16)
        self._length_slider.valueChanged.connect(self._length_spin.setValue)
        self._length_spin.valueChanged.connect(self._length_slider.setValue)
        self._password_row.addWidget(self._length_spin)
        layout.addLayout(self._password_row)

        self._charset_row = QHBoxLayout()
        self._lowercase_check = QCheckBox("a-z")
        self._lowercase_check.setChecked(True)
        self._uppercase_check = QCheckBox("A-Z")
        self._uppercase_check.setChecked(True)
        self._digits_check = QCheckBox("0-9")
        self._digits_check.setChecked(True)
        self._symbols_check = QCheckBox("Symbols")
        self._symbols_check.setChecked(True)
        self._exclude_ambiguous_check = QCheckBox("Exclude ambiguous (il1Lo0O)")
        for check in (
            self._lowercase_check,
            self._uppercase_check,
            self._digits_check,
            self._symbols_check,
            self._exclude_ambiguous_check,
        ):
            self._charset_row.addWidget(check)
        self._charset_row.addStretch(1)
        layout.addLayout(self._charset_row)

        self._passphrase_row = QHBoxLayout()
        self._passphrase_row.addWidget(QLabel("Words"))
        self._word_count_spin = QSpinBox()
        self._word_count_spin.setRange(2, 12)
        self._word_count_spin.setValue(4)
        self._passphrase_row.addWidget(self._word_count_spin)
        self._passphrase_row.addWidget(QLabel("Separator"))
        self._separator_combo = QComboBox()
        self._separator_combo.addItems(["-", "_", ".", " "])
        self._passphrase_row.addWidget(self._separator_combo)
        self._capitalize_check = QCheckBox("Capitalize")
        self._passphrase_row.addWidget(self._capitalize_check)
        self._passphrase_row.addStretch(1)
        layout.addLayout(self._passphrase_row)

        layout.addWidget(QLabel("OUTPUT"))
        self._output = QLineEdit()
        self._output.setReadOnly(True)
        self._output.setObjectName("passwordOutput")
        layout.addWidget(self._output)

        self._strength_label = QLabel("")
        layout.addWidget(self._strength_label)

        self._set_passphrase_row_visible(False)

    def build_actions(self, layout: QHBoxLayout) -> None:
        generate_button = QPushButton("Generate")
        generate_button.setObjectName("primaryButton")
        generate_button.clicked.connect(self._generate)
        layout.addWidget(generate_button)
        layout.addStretch(1)

        copy_button = QPushButton("Copy")
        copy_button.clicked.connect(self._copy)
        layout.addWidget(copy_button)

    def _on_mode_toggled(self, checked: bool) -> None:
        self._set_passphrase_row_visible(not checked)

    def _set_passphrase_row_visible(self, visible: bool) -> None:
        for i in range(self._password_row.count()):
            widget = self._password_row.itemAt(i).widget()
            if widget:
                widget.setVisible(not visible)
        for i in range(self._charset_row.count()):
            widget = self._charset_row.itemAt(i).widget()
            if widget:
                widget.setVisible(not visible)
        for i in range(self._passphrase_row.count()):
            widget = self._passphrase_row.itemAt(i).widget()
            if widget:
                widget.setVisible(visible)

    def _generate(self) -> None:
        if self._password_radio.isChecked():
            options = PasswordOptions(
                length=self._length_spin.value(),
                lowercase=self._lowercase_check.isChecked(),
                uppercase=self._uppercase_check.isChecked(),
                digits=self._digits_check.isChecked(),
                symbols=self._symbols_check.isChecked(),
                exclude_ambiguous=self._exclude_ambiguous_check.isChecked(),
            )
            try:
                value = generate_password(options)
            except ValueError as exc:
                show_toast(self, str(exc), "warning")
                return

            pool_size = sum(
                len(charset)
                for enabled, charset in (
                    (options.lowercase, LOWERCASE),
                    (options.uppercase, UPPERCASE),
                    (options.digits, DIGITS),
                    (options.symbols, SYMBOLS),
                )
                if enabled
            )
            entropy = password_entropy_bits(options.length, pool_size)
            self._strength_label.setText(
                f"Strength: {strength_label(entropy)} (~{entropy:.0f} bits)"
            )
        else:
            value = generate_passphrase(
                word_count=self._word_count_spin.value(),
                separator=self._separator_combo.currentText(),
                capitalize=self._capitalize_check.isChecked(),
            )
            self._strength_label.setText("")

        self._output.setText(value)
        show_toast(self, "Generated", "success")

    def _copy(self) -> None:
        text = self._output.text()
        if not text:
            show_toast(self, "Nothing to copy", "warning")
            return
        self.copy_to_clipboard(text)
        show_toast(self, "Copied to clipboard", "success")
