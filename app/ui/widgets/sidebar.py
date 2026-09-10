"""Primary navigation: Home, Favorites, Tools by category, History, Settings."""

from __future__ import annotations

from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.core.constants import COLLAPSED_SIDEBAR_WIDTH, DEFAULT_SIDEBAR_WIDTH, TOOL_CATEGORIES
from app.ui.icons import category_icon_name, icon, nav_icon_name
from app.ui.theme import current_palette

ROUTE_HOME = "home"
ROUTE_FAVORITES = "favorites"
ROUTE_HISTORY = "history"
ROUTE_SETTINGS = "settings"

_ICON_SIZE = 17


def category_route(category: str) -> str:
    return f"category:{category}"


class Sidebar(QWidget):
    navigate = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("sidebar")
        self._collapsed = False
        self._buttons: dict[str, QPushButton] = {}
        self._labels: dict[str, str] = {}
        self._icon_names: dict[str, str] = {}
        self._active_route = ROUTE_HOME

        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 12, 8, 12)
        outer.setSpacing(2)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        content = QWidget()
        self._nav_layout = QVBoxLayout(content)
        self._nav_layout.setContentsMargins(0, 0, 0, 0)
        self._nav_layout.setSpacing(2)
        scroll.setWidget(content)
        outer.addWidget(scroll, stretch=1)

        self._add_nav_button(ROUTE_HOME, "Home", nav_icon_name("home"))
        self._add_nav_button(ROUTE_FAVORITES, "Favorites", nav_icon_name("favorites"))

        self._add_section_label("Tools")
        for category in TOOL_CATEGORIES:
            self._add_nav_button(category_route(category), category, category_icon_name(category))

        self._add_divider()
        self._add_nav_button(ROUTE_HISTORY, "History", nav_icon_name("history"))
        self._add_nav_button(ROUTE_SETTINGS, "Settings", nav_icon_name("settings"))
        self._nav_layout.addStretch(1)

        self.set_active(ROUTE_HOME)
        self.setFixedWidth(DEFAULT_SIDEBAR_WIDTH)

    def _add_section_label(self, text: str) -> None:
        label = QLabel(text)
        label.setObjectName("sidebarSectionLabel")
        label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self._nav_layout.addWidget(label)

    def _add_divider(self) -> None:
        # Plain QSS-styled bar — NOT QFrame.Shape.HLine, which paints its own
        # native sunken/plain line on top of (and fighting) the stylesheet.
        divider = QFrame()
        divider.setObjectName("sidebarDivider")
        divider.setFixedHeight(1)
        self._nav_layout.addWidget(divider)

    def _add_nav_button(self, route: str, label: str, icon_name: str) -> None:
        button = QPushButton(label)
        button.setObjectName("sidebarNavButton")
        button.setCheckable(True)
        button.setProperty("active", False)
        button.setIconSize(QSize(_ICON_SIZE, _ICON_SIZE))
        button.clicked.connect(lambda: self._on_nav_clicked(route))
        self._nav_layout.addWidget(button)
        self._buttons[route] = button
        self._labels[route] = label
        self._icon_names[route] = icon_name
        self._restyle_icon(route)

    def _restyle_icon(self, route: str) -> None:
        button = self._buttons[route]
        color = self._text_color(active=button.property("active") is True)
        button.setIcon(icon(self._icon_names[route], color, _ICON_SIZE))

    def _text_color(self, active: bool) -> str:
        app = QApplication.instance()
        palette = current_palette(app) if app else None
        if palette is None:
            return "#9AA3B7"
        return palette.accent if active else palette.text_secondary

    def _on_nav_clicked(self, route: str) -> None:
        self.set_active(route)
        self.navigate.emit(route)

    def set_active(self, route: str) -> None:
        for r, button in self._buttons.items():
            active = r == route
            button.setChecked(active)
            button.setProperty("active", active)
            button.style().unpolish(button)
            button.style().polish(button)
            self._restyle_icon(r)
        self._active_route = route

    def refresh_icons(self) -> None:
        """Call after a theme/accent change so nav icons pick up the new colors."""
        for route in self._buttons:
            self._restyle_icon(route)

    def toggle_collapsed(self) -> None:
        self._collapsed = not self._collapsed
        width = COLLAPSED_SIDEBAR_WIDTH if self._collapsed else DEFAULT_SIDEBAR_WIDTH
        self.setFixedWidth(width)
        for route, button in self._buttons.items():
            if self._collapsed:
                button.setText("")
                button.setToolTip(self._labels[route])
            else:
                button.setText(self._labels[route])
                button.setToolTip("")
