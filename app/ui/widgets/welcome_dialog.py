"""One-time first-run welcome dialog. Shown once, then never again."""

from __future__ import annotations

from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QWidget

from app.core.constants import APP_DISPLAY_NAME
from app.ui import shortcuts as sc


class WelcomeDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("welcomeDialog")
        self.setWindowTitle(f"Welcome to {APP_DISPLAY_NAME}")
        self.setModal(True)
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel(f"Welcome to {APP_DISPLAY_NAME}")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        body = QLabel(
            "Every tool runs locally and offline — nothing you type or open is "
            "ever transmitted, and there's no telemetry.\n\n"
            f"Press {sc.COMMAND_PALETTE} anytime to jump straight to a tool or "
            "action. Optional history and clipboard tracking can be turned on "
            "in Settings > Privacy — both are off by default."
        )
        body.setWordWrap(True)
        layout.addWidget(body)

        button = QPushButton("Get Started")
        button.setObjectName("primaryButton")
        button.clicked.connect(self.accept)
        layout.addWidget(button)
