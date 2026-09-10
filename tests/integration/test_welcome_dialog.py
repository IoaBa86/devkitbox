from __future__ import annotations

from PySide6.QtWidgets import QDialog, QPushButton

from app.ui.widgets.welcome_dialog import WelcomeDialog


def test_welcome_dialog_get_started_accepts(qtbot):
    dialog = WelcomeDialog()
    qtbot.addWidget(dialog)

    button = dialog.findChild(QPushButton)
    button.click()

    assert dialog.result() == QDialog.DialogCode.Accepted
