"""Vector icon set for DevKitBox.

Every icon is a small hand-authored line-drawing (24x24, stroke-based) so it
renders identically everywhere and can be recolored per-theme/per-state at
paint time — unlike Unicode glyphs, which vary by installed font and are the
single biggest visual "tell" of an unstyled desktop app.
"""

from __future__ import annotations

from functools import lru_cache

from PySide6.QtCore import QByteArray, QRectF, QSize, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

from app.core.paths import get_resource_root

_ASSETS_DIR = get_resource_root() / "assets" / "icons"

# Each path is the inner content of a 24x24 stroked SVG (round caps/joins).
_ICON_PATHS: dict[str, str] = {
    "home": '<path d="M4 11.5 12 4l8 7.5"/><path d="M6 10v9h5v-5h2v5h5v-9"/>',
    "star": ('<path d="M12 3.4l2.4 5 5.4.6-4 3.7 1 5.4L12 15.4l-4.8 2.7 1-5.4-4-3.7 5.4-.6z"/>'),
    "star_filled": (
        '<path d="M12 3.4l2.4 5 5.4.6-4 3.7 1 5.4L12 15.4l-4.8 2.7 1-5.4-4-3.7 '
        '5.4-.6z" fill="currentColor" stroke="none"/>'
    ),
    "history": '<path d="M4 8h6M4 8V4"/><path d="M4 8a8 8 0 1 1 2 8.4"/><path d="M12 9v4l3 2"/>',
    "settings": (
        '<circle cx="12" cy="12" r="3"/>'
        '<path d="M12 3v3M12 18v3M4.4 6.4l2.1 2.1M17.5 15.5l2.1 2.1'
        'M3 12h3M18 12h3M4.4 17.6l2.1-2.1M17.5 8.5l2.1-2.1"/>'
    ),
    "search": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M20 20l-5-5"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "brand": '<path d="M9 6.5 4.5 12 9 17.5"/><path d="M15 6.5l4.5 5.5-4.5 5.5"/>',
    "chevron_right": '<path d="M9 5l7 7-7 7"/>',
    "folder": '<path d="M3 7h6l2 2h10v10H3z"/>',
    # Straight-line paths (no curves) — curved/complex glyphs like the old
    # braces and star-polygon sparkle degrade into an indistinct blob at the
    # ~18px sizes these render at, so every icon here favors straight strokes.
    "braces": '<path d="M4 5h16v14H4z"/><path d="M8 10l3 2-3 2"/><path d="M13 16h4"/>',
    "swap": '<path d="M4 8h11M12 4l4 4-4 4"/><path d="M20 16H9M12 12l-4 4 4 4"/>',
    "lines": '<path d="M5 6h14M5 12h14M5 18h9"/>',
    "sparkle": '<path d="M12 3v6M12 15v6M3 12h6M15 12h6M6.5 6.5l3.5 3.5M14 14l3.5 3.5M17.5 6.5 14 10M10 14l-3.5 3.5"/>',
    "check": '<path d="M4 12.5l5 5L20 6"/>',
    "warning": '<path d="M12 4 21 19H3z"/><path d="M12 10v4"/><path d="M12 16.3v.2"/>',
    "close": '<path d="M5 5l14 14M19 5 5 19"/>',
    "dot": '<circle cx="12" cy="12" r="4" fill="currentColor" stroke="none"/>',
    "network": '<circle cx="5" cy="5" r="2"/><circle cx="19" cy="5" r="2"/><circle cx="12" cy="19" r="2"/><path d="M6.5 6.5 11 17M17.5 6.5 13 17M7 5h10"/>',
    "palette": '<path d="M4 4h8v8H4z"/><path d="M12 4h8v8h-8z"/><path d="M4 12h8v8H4z"/><path d="M12 12h8v8h-8z"/>',
}

CATEGORY_ICON: dict[str, str] = {
    "Development": "braces",
    "Encoding": "swap",
    "Text": "lines",
    "Generators": "sparkle",
    "Files": "folder",
    "Network": "network",
    "Design": "palette",
}

NAV_ICON: dict[str, str] = {
    "home": "home",
    "favorites": "star",
    "history": "history",
    "settings": "settings",
}


def _render(name: str, color: str, size: int) -> QPixmap:
    body = _ICON_PATHS.get(name, _ICON_PATHS["dot"])
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="2.3" stroke-linecap="round" '
        f'stroke-linejoin="round" color="{color}">{body}</svg>'
    )
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    ratio = 2  # render at 2x for crisp scaling on hi-DPI displays
    pixmap = QPixmap(QSize(size, size) * ratio)
    pixmap.fill(Qt.GlobalColor.transparent)
    pixmap.setDevicePixelRatio(ratio)
    painter = QPainter(pixmap)
    # QSvgRenderer.render(painter) with no target rect paints at the SVG's
    # native viewBox size instead of scaling to fill the pixmap — every icon
    # ends up a cropped, misaligned fragment. Pass an explicit target rect.
    renderer.render(painter, QRectF(0, 0, size, size))
    painter.end()
    return pixmap


@lru_cache(maxsize=256)
def _cached_pixmap(name: str, color: str, size: int) -> QPixmap:
    return _render(name, color, size)


def icon_pixmap(name: str, color: str, size: int = 18) -> QPixmap:
    return _cached_pixmap(name, color, size)


def icon(name: str, color: str, size: int = 18) -> QIcon:
    return QIcon(icon_pixmap(name, color, size))


def app_icon() -> QIcon:
    svg_path = _ASSETS_DIR / "app_icon.svg"
    if svg_path.exists():
        return QIcon(str(svg_path))
    return QIcon()


def category_icon_name(category: str) -> str:
    return CATEGORY_ICON.get(category, "dot")


def nav_icon_name(key: str) -> str:
    return NAV_ICON.get(key, "dot")
