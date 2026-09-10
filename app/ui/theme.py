"""Design tokens and stylesheet generation for the dark/light theme system.

Palette: near-black graphite surfaces with a signal-violet accent (dark),
mirrored on a soft off-white in light mode. Depth comes from a small stack
of surface tiers (bg -> surface -> surface_raised) plus real drop shadows
via :func:`elevate`, since Qt's stylesheets have no box-shadow property.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication, QGraphicsDropShadowEffect, QWidget

MONOSPACE_FONT_FAMILY = "Cascadia Code, Consolas, 'Courier New', monospace"
UI_FONT_FAMILY = "Segoe UI, Inter, sans-serif"
DISPLAY_FONT_FAMILY = "Segoe UI Semibold, Segoe UI, sans-serif"


@dataclass(frozen=True)
class Palette:
    bg: str
    surface: str
    surface_raised: str
    surface_hover: str
    border: str
    border_strong: str
    text: str
    text_secondary: str
    text_muted: str
    accent: str
    accent_soft: str
    accent_text: str
    danger: str
    success: str
    warning: str
    shadow: str


def dark_palette(accent: str) -> Palette:
    return Palette(
        bg="#0E1016",
        surface="#161922",
        surface_raised="#1C2029",
        surface_hover="#232733",
        border="#272B36",
        border_strong="#343947",
        text="#EDEFF4",
        text_secondary="#9AA3B7",
        text_muted="#646C7E",
        accent=accent,
        accent_soft=_with_alpha(accent, 0.16),
        accent_text="#FFFFFF",
        danger="#FF6B6B",
        success="#34D399",
        warning="#FFB454",
        shadow="rgba(0, 0, 0, 90)",
    )


def light_palette(accent: str) -> Palette:
    return Palette(
        bg="#F3F4F8",
        surface="#FFFFFF",
        surface_raised="#FFFFFF",
        surface_hover="#EEF0F6",
        border="#E3E5EE",
        border_strong="#CDD1E0",
        text="#161822",
        text_secondary="#585F72",
        text_muted="#8B90A0",
        accent=accent,
        accent_soft=_with_alpha(accent, 0.10),
        accent_text="#FFFFFF",
        danger="#D8433B",
        success="#1E9A5C",
        warning="#B87A16",
        shadow="rgba(30, 34, 54, 35)",
    )


def _with_alpha(hex_color: str, alpha: float) -> str:
    color = QColor(hex_color)
    return f"rgba({color.red()}, {color.green()}, {color.blue()}, {alpha})"


def resolve_theme_mode(theme: str) -> str:
    """Resolve 'system' to 'light' or 'dark' using the OS color scheme."""
    if theme != "system":
        return theme
    app = QApplication.instance()
    if app is None:
        return "dark"
    hints = app.styleHints()
    try:
        from PySide6.QtCore import Qt

        return "dark" if hints.colorScheme() == Qt.ColorScheme.Dark else "light"
    except Exception:
        return "dark"


def elevate(widget: QWidget, blur: int = 24, y_offset: int = 6, strength: int = 90) -> None:
    """Applies a soft drop shadow so a card/panel reads as lifted off the canvas."""
    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(blur)
    effect.setOffset(0, y_offset)
    effect.setColor(QColor(0, 0, 0, strength))
    widget.setGraphicsEffect(effect)


def build_stylesheet(p: Palette) -> str:
    return f"""
    * {{
        font-family: {UI_FONT_FAMILY};
        color: {p.text};
        outline: none;
    }}
    QToolTip {{
        background-color: {p.surface_raised};
        color: {p.text};
        border: 1px solid {p.border_strong};
        border-radius: 6px;
        padding: 6px 8px;
    }}
    QWidget {{
        background-color: {p.bg};
    }}
    QMainWindow, #centralWidget {{
        background-color: {p.bg};
    }}
    /* QLabel must stay transparent — otherwise it paints its own opaque
       QWidget background (bg) as a mismatched rectangle on top of whatever
       surface color its parent (e.g. a card) actually uses. */
    QLabel, QCheckBox, QRadioButton {{
        background: transparent;
    }}

    /* -- Command bar (top) ------------------------------------------- */
    #topBar {{
        background-color: {p.surface_raised};
        border-bottom: 1px solid {p.border};
    }}
    #brandTitle {{
        font-family: {DISPLAY_FONT_FAMILY};
        font-size: 15px;
        font-weight: 700;
        letter-spacing: 0.2px;
    }}
    #chromeButton {{
        background: transparent;
        border: 1px solid transparent;
        border-radius: 8px;
        padding: 6px;
    }}
    #chromeButton:hover {{
        background-color: {p.surface_hover};
        border: 1px solid {p.border};
    }}

    /* -- Sidebar -------------------------------------------------------*/
    #sidebar {{
        background-color: {p.surface};
        border-right: 1px solid {p.border};
    }}
    #sidebarNavButton {{
        text-align: left;
        padding: 8px 10px;
        border-radius: 8px;
        border: none;
        background: transparent;
        color: {p.text_secondary};
        font-size: 13px;
    }}
    #sidebarNavButton:hover {{
        background-color: {p.surface_hover};
        color: {p.text};
    }}
    #sidebarNavButton[active="true"] {{
        background-color: {p.accent_soft};
        color: {p.accent};
        font-weight: 600;
    }}
    #sidebarSectionLabel {{
        color: {p.text_muted};
        font-size: 10.5px;
        font-weight: 700;
        letter-spacing: 1.2px;
        padding: 14px 10px 6px 10px;
    }}
    #sidebarDivider {{
        background-color: {p.border};
        max-height: 1px;
        min-height: 1px;
        margin: 8px 10px;
    }}

    /* -- Status bar ------------------------------------------------- */
    QStatusBar {{
        background-color: {p.surface};
        border-top: 1px solid {p.border};
        color: {p.text_muted};
        font-size: 11.5px;
    }}
    QStatusBar::item {{ border: none; }}

    /* -- Inputs -------------------------------------------------------*/
    QLineEdit, QPlainTextEdit, QTextEdit, QComboBox, QSpinBox {{
        background-color: {p.surface};
        border: 1px solid {p.border};
        border-radius: 8px;
        padding: 6px 10px;
        selection-background-color: {p.accent};
        selection-color: {p.accent_text};
    }}
    QLineEdit:hover, QComboBox:hover, QSpinBox:hover {{
        border: 1px solid {p.border_strong};
    }}
    QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {{
        border: 1px solid {p.accent};
    }}
    QLineEdit:read-only, QPlainTextEdit[readOnly="true"] {{
        color: {p.text_secondary};
    }}
    QComboBox::drop-down {{ border: none; width: 22px; }}
    QComboBox QAbstractItemView {{
        background-color: {p.surface_raised};
        border: 1px solid {p.border_strong};
        selection-background-color: {p.accent_soft};
        selection-color: {p.accent};
        outline: none;
    }}

    #searchBox {{
        background-color: {p.surface};
        border: 1px solid {p.border};
        border-radius: 9px;
        padding: 6px 10px 6px 34px;
        min-height: 20px;
    }}
    #searchBox:focus {{
        border: 1px solid {p.accent};
    }}

    /* -- Buttons ------------------------------------------------------*/
    QPushButton {{
        background-color: {p.surface_raised};
        border: 1px solid {p.border};
        border-radius: 8px;
        padding: 7px 14px;
        color: {p.text};
        font-weight: 500;
    }}
    QPushButton:hover {{
        border: 1px solid {p.border_strong};
        background-color: {p.surface_hover};
    }}
    QPushButton:pressed {{
        background-color: {p.border};
    }}
    QPushButton:disabled {{
        color: {p.text_muted};
    }}
    QPushButton#primaryButton {{
        background-color: {p.accent};
        color: {p.accent_text};
        border: none;
        font-weight: 600;
    }}
    QPushButton#primaryButton:hover {{
        background-color: {p.accent};
    }}
    QCheckBox, QRadioButton {{
        spacing: 8px;
        color: {p.text_secondary};
    }}
    QCheckBox::indicator, QRadioButton::indicator {{
        width: 15px;
        height: 15px;
        border: 1.5px solid {p.border_strong};
        background-color: {p.surface};
    }}
    QCheckBox::indicator {{
        border-radius: 4px;
    }}
    QRadioButton::indicator {{
        border-radius: 8px;
    }}
    QCheckBox::indicator:hover, QRadioButton::indicator:hover {{
        border: 1.5px solid {p.accent};
    }}
    QCheckBox::indicator:checked {{
        background-color: {p.accent};
        border: 1.5px solid {p.accent};
    }}
    QRadioButton::indicator:checked {{
        background-color: {p.surface};
        border: 4px solid {p.accent};
    }}
    #favoriteButton {{
        border: none;
        background: transparent;
        padding: 2px 4px;
    }}

    /* -- Typography helpers -------------------------------------------*/
    #pageTitle {{
        font-family: {DISPLAY_FONT_FAMILY};
        font-size: 21px;
        font-weight: 700;
        letter-spacing: 0.1px;
    }}
    #sectionHeading {{
        font-family: {DISPLAY_FONT_FAMILY};
        font-size: 14px;
        font-weight: 700;
    }}
    #sectionRule {{
        background-color: {p.accent};
        border-radius: 2px;
    }}
    #toolBreadcrumb {{
        color: {p.text_muted};
        font-size: 11.5px;
        font-weight: 600;
        letter-spacing: 0.3px;
    }}
    #toolDescription {{
        color: {p.text_secondary};
        font-size: 12.5px;
    }}

    /* -- Cards ----------------------------------------------------------*/
    #cardWidget {{
        background-color: {p.surface};
        border: 1px solid {p.border};
        border-radius: 12px;
    }}
    #cardWidget:hover {{
        border: 1px solid {p.accent};
        background-color: {p.surface_hover};
    }}
    #iconBadge {{
        background-color: {p.accent};
        border-radius: 9px;
    }}
    #emptyBadge {{
        background-color: {p.surface_hover};
        border: 1px solid {p.border};
        border-radius: 14px;
    }}

    /* -- Empty states ---------------------------------------------------*/
    #emptyStateTitle {{
        color: {p.text};
        font-size: 13.5px;
        font-weight: 600;
    }}
    #emptyStateSubtitle {{
        color: {p.text_muted};
        font-size: 12px;
    }}

    /* -- Toast ------------------------------------------------------- */
    #toast {{
        background-color: {p.surface_raised};
        border: 1px solid {p.border_strong};
        border-radius: 9px;
        color: {p.text};
        padding: 9px 16px;
        font-size: 12.5px;
        font-weight: 500;
    }}

    /* -- Tables --------------------------------------------------------*/
    QTableWidget {{
        background-color: {p.surface};
        border: 1px solid {p.border};
        border-radius: 8px;
        gridline-color: {p.border};
    }}
    QHeaderView::section {{
        background-color: {p.surface_raised};
        color: {p.text_muted};
        border: none;
        border-bottom: 1px solid {p.border};
        padding: 6px 8px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }}
    QTableWidget::item {{
        padding: 4px 6px;
    }}
    QTableWidget::item:selected {{
        background-color: {p.accent_soft};
        color: {p.text};
    }}
    QTabWidget::pane {{
        border: 1px solid {p.border};
        border-radius: 8px;
        top: -1px;
    }}
    QTabBar::tab {{
        background: transparent;
        color: {p.text_secondary};
        padding: 8px 14px;
        border: none;
    }}
    QTabBar::tab:selected {{
        color: {p.accent};
        font-weight: 600;
        border-bottom: 2px solid {p.accent};
    }}
    QProgressBar {{
        background-color: {p.surface};
        border: 1px solid {p.border};
        border-radius: 6px;
        text-align: center;
        color: {p.text_secondary};
        height: 10px;
    }}
    QProgressBar::chunk {{
        background-color: {p.accent};
        border-radius: 6px;
    }}

    /* -- Scrollbars ------------------------------------------------- */
    QScrollBar:vertical {{
        background: transparent;
        width: 10px;
        margin: 2px;
    }}
    QScrollBar::handle:vertical {{
        background: {p.border_strong};
        border-radius: 5px;
        min-height: 24px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {p.text_muted};
    }}
    QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
    QScrollBar:horizontal {{
        background: transparent;
        height: 10px;
        margin: 2px;
    }}
    QScrollBar::handle:horizontal {{
        background: {p.border_strong};
        border-radius: 5px;
        min-width: 24px;
    }}
    """


def apply_theme(app: QApplication, theme: str, accent: str) -> None:
    mode = resolve_theme_mode(theme)
    palette_tokens = dark_palette(accent) if mode == "dark" else light_palette(accent)

    qt_palette = QPalette()
    qt_palette.setColor(QPalette.ColorRole.Window, QColor(palette_tokens.bg))
    qt_palette.setColor(QPalette.ColorRole.WindowText, QColor(palette_tokens.text))
    qt_palette.setColor(QPalette.ColorRole.Base, QColor(palette_tokens.surface))
    qt_palette.setColor(QPalette.ColorRole.Text, QColor(palette_tokens.text))
    qt_palette.setColor(QPalette.ColorRole.Button, QColor(palette_tokens.surface_raised))
    qt_palette.setColor(QPalette.ColorRole.ButtonText, QColor(palette_tokens.text))
    qt_palette.setColor(QPalette.ColorRole.Highlight, QColor(palette_tokens.accent))
    qt_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(palette_tokens.accent_text))
    qt_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(palette_tokens.surface_raised))
    qt_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(palette_tokens.text))
    app.setPalette(qt_palette)
    app.setStyleSheet(build_stylesheet(palette_tokens))
    app.setProperty("dkbPalette", palette_tokens)


def current_palette(app: QApplication) -> Palette | None:
    return app.property("dkbPalette")
