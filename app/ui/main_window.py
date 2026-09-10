"""Application shell: title bar, sidebar, routed content area, status bar."""

from __future__ import annotations

from PySide6.QtCore import QSize, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.core.app_context import AppContext
from app.core.constants import (
    APP_DISPLAY_NAME,
    APP_VERSION,
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
)
from app.ui import shortcuts as sc
from app.ui.icons import app_icon, icon, icon_pixmap
from app.ui.pages.favorites_page import FavoritesPage
from app.ui.pages.history_page import HistoryPage
from app.ui.pages.home_page import HomePage
from app.ui.pages.settings_page import SettingsPage
from app.ui.theme import apply_theme, current_palette
from app.ui.widgets.command_palette import CommandPalette, PaletteCommand
from app.ui.widgets.empty_state import EmptyState
from app.ui.widgets.responsive_grid import ResponsiveGrid
from app.ui.widgets.search_box import SearchBox
from app.ui.widgets.sidebar import (
    ROUTE_FAVORITES,
    ROUTE_HISTORY,
    ROUTE_HOME,
    ROUTE_SETTINGS,
    Sidebar,
    category_route,
)
from app.ui.widgets.toast import show_toast
from app.ui.widgets.tool_card import ToolCard
from app.ui.widgets.welcome_dialog import WelcomeDialog


class MainWindow(QMainWindow):
    def __init__(self, context: AppContext) -> None:
        super().__init__()
        self.context = context
        self.setWindowTitle(APP_DISPLAY_NAME)
        self.setWindowIcon(app_icon())
        self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        self.setMinimumSize(760, 560)

        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = Sidebar()
        root.addWidget(self.sidebar)

        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(0)
        root.addLayout(right, stretch=1)

        right.addWidget(self._build_topbar())

        self._stack = QStackedWidget()
        right.addWidget(self._stack, stretch=1)

        self._routes: dict[str, int] = {}
        self._category_pages: dict[str, QWidget] = {}
        self._active_tool_id: str | None = None

        self.home_page = HomePage(context)
        self.favorites_page = FavoritesPage(context)
        self.history_page = HistoryPage(context)
        self.settings_page = SettingsPage(context)

        self._add_page(ROUTE_HOME, self.home_page)
        self._add_page(ROUTE_FAVORITES, self.favorites_page)
        self._add_page(ROUTE_HISTORY, self.history_page)
        self._add_page(ROUTE_SETTINGS, self.settings_page)

        self._search_results_page, self._search_results_layout = self._build_list_page(
            "Search Results"
        )
        self._search_route = "search"
        self._add_page(self._search_route, self._search_results_page)
        self._last_route = ROUTE_HOME
        self._pre_search_route = ROUTE_HOME

        self.home_page.open_tool.connect(self.open_tool)
        self.home_page.open_category.connect(self._navigate)
        self.favorites_page.open_tool.connect(self.open_tool)
        self.history_page.open_tool.connect(self.open_tool)
        self.settings_page.theme_changed.connect(self._apply_theme)
        self.sidebar.navigate.connect(self._navigate)

        self._build_status_bar()
        self._register_shortcuts()

        self._navigate(ROUTE_HOME)
        self._apply_theme()
        QTimer.singleShot(0, self._maybe_show_welcome)

    def _maybe_show_welcome(self) -> None:
        if self.context.settings.has_completed_onboarding:
            return
        WelcomeDialog(self).exec()
        self.context.settings.has_completed_onboarding = True
        self.context.settings_service.set("has_completed_onboarding", True)

    # -- Chrome ----------------------------------------------------------

    def _build_topbar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("topBar")
        bar.setFixedHeight(56)
        topbar = QHBoxLayout(bar)
        topbar.setContentsMargins(16, 10, 16, 10)
        topbar.setSpacing(10)

        self._collapse_button = self._chrome_button("Toggle sidebar")
        self._collapse_button.clicked.connect(self.sidebar.toggle_collapsed)
        topbar.addWidget(self._collapse_button)

        self._brand_icon_label = QLabel()
        self._brand_icon_label.setFixedSize(20, 20)
        topbar.addWidget(self._brand_icon_label)

        title = QLabel(APP_DISPLAY_NAME)
        title.setObjectName("brandTitle")
        topbar.addWidget(title)
        topbar.addStretch(1)

        self.search_box = SearchBox()
        self.search_box.setMinimumWidth(160)
        self.search_box.setMaximumWidth(360)
        self.search_box.query_changed.connect(self._on_search)
        topbar.addWidget(self.search_box, stretch=1)

        self._settings_button = self._chrome_button("Settings")
        self._settings_button.clicked.connect(lambda: self._navigate(ROUTE_SETTINGS))
        topbar.addWidget(self._settings_button)

        return bar

    @staticmethod
    def _chrome_button(tooltip: str) -> QPushButton:
        button = QPushButton()
        button.setObjectName("chromeButton")
        button.setFixedSize(32, 32)
        button.setIconSize(QSize(17, 17))
        button.setToolTip(tooltip)
        return button

    def _build_status_bar(self) -> None:
        status = self.statusBar()
        status.showMessage("Ready")
        version_label = QLabel(f"{APP_DISPLAY_NAME} {APP_VERSION}")
        status.addPermanentWidget(version_label)

    def _register_shortcuts(self) -> None:
        QShortcut(QKeySequence(sc.OPEN_SETTINGS), self, lambda: self._navigate(ROUTE_SETTINGS))
        QShortcut(QKeySequence(sc.FOCUS_SEARCH), self, self.search_box.setFocus)
        QShortcut(QKeySequence(sc.COMMAND_PALETTE), self, self._open_command_palette)

    def _open_command_palette(self) -> None:
        commands = [
            PaletteCommand("Go to Home", "Navigation", lambda: self._navigate(ROUTE_HOME)),
            PaletteCommand(
                "Go to Favorites", "Navigation", lambda: self._navigate(ROUTE_FAVORITES)
            ),
            PaletteCommand("Go to History", "Navigation", lambda: self._navigate(ROUTE_HISTORY)),
            PaletteCommand("Go to Settings", "Navigation", lambda: self._navigate(ROUTE_SETTINGS)),
            PaletteCommand("Toggle Sidebar", "View", self.sidebar.toggle_collapsed),
        ]
        palette = CommandPalette(self.context, commands, self.open_tool, self)
        geometry = self.geometry()
        x = geometry.x() + (geometry.width() - palette.minimumWidth()) // 2
        y = geometry.y() + 120
        palette.move(x, y)
        palette.exec()

    # -- Routing -----------------------------------------------------------

    def _add_page(self, route: str, widget: QWidget) -> None:
        index = self._stack.addWidget(widget)
        self._routes[route] = index

    def _navigate(self, route: str) -> None:
        if route.startswith("category:"):
            category = route.split(":", 1)[1]
            self._show_category(category)
        elif route in self._routes:
            self._stack.setCurrentIndex(self._routes[route])
        else:
            return
        self.sidebar.set_active(route)
        self._last_route = route
        for page in (self.home_page, self.favorites_page, self.history_page):
            if hasattr(page, "refresh"):
                page.refresh()

    def _show_category(self, category: str) -> None:
        if category not in self._category_pages:
            page = self._build_category_page(category)
            self._category_pages[category] = page
            index = self._stack.addWidget(page)
            self._routes[category_route(category)] = index
        else:
            self._refresh_category_page(category)
        self._stack.setCurrentIndex(self._routes[category_route(category)])

    @staticmethod
    def _build_list_page(title: str) -> tuple[QWidget, QVBoxLayout]:
        page = QWidget()
        outer = QVBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        outer.addWidget(scroll)

        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)
        title_label = QLabel(title)
        title_label.setObjectName("pageTitle")
        layout.addWidget(title_label)

        content = QVBoxLayout()
        layout.addLayout(content)
        layout.addStretch(1)
        scroll.setWidget(body)
        return page, content

    def _build_category_page(self, category: str) -> QWidget:
        page, content = self._build_list_page(category)
        page.content_layout = content  # type: ignore[attr-defined]
        self._fill_category_content(content, category)
        return page

    def _refresh_category_page(self, category: str) -> None:
        page = self._category_pages[category]
        content: QVBoxLayout = page.content_layout  # type: ignore[attr-defined]
        while content.count():
            item = content.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._fill_category_content(content, category)

    def _fill_category_content(self, content: QVBoxLayout, category: str) -> None:
        tools = self.context.tool_registry.get_by_category(category)
        if not tools:
            content.addWidget(
                EmptyState("dot", "No tools here yet.", "This category is still growing.")
            )
            return
        grid = ResponsiveGrid(min_item_width=200, max_columns=4)
        cards = []
        for metadata in tools:
            card = ToolCard(metadata)
            card.clicked.connect(self.open_tool)
            cards.append(card)
        grid.set_items(cards)
        content.addWidget(grid)

    def open_tool(self, tool_id: str) -> None:
        tool_cls = self.context.tool_registry.get_by_id(tool_id)
        if tool_cls is None:
            show_toast(self, "That tool isn't available yet.", "warning")
            return
        self.context.history_service.record_recent(tool_id)
        route = f"tool:{tool_id}"
        if route not in self._routes:
            widget = tool_cls(self.context)
            index = self._stack.addWidget(widget)
            self._routes[route] = index
        self._stack.setCurrentIndex(self._routes[route])
        self._active_tool_id = tool_id
        self._last_route = route

    def _on_search(self, query: str) -> None:
        query = query.strip()
        on_results_page = self._stack.currentWidget() is self._search_results_page

        if not query:
            if on_results_page:
                self._navigate(self._pre_search_route)
            return

        if not on_results_page:
            self._pre_search_route = self._last_route

        while self._search_results_layout.count():
            item = self._search_results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        results = self.context.tool_registry.search(query)
        if not results:
            self._search_results_layout.addWidget(
                EmptyState("search", "No tools found.", "Try a different search term.")
            )
        else:
            grid = ResponsiveGrid(min_item_width=200, max_columns=4)
            cards = []
            for metadata in results:
                card = ToolCard(metadata)
                card.clicked.connect(self.open_tool)
                cards.append(card)
            grid.set_items(cards)
            self._search_results_layout.addWidget(grid)

        self._stack.setCurrentIndex(self._routes[self._search_route])

    # -- Theme / lifecycle -------------------------------------------------

    def _apply_theme(self) -> None:
        app = QApplication.instance()
        apply_theme(app, self.context.settings.theme, self.context.settings.accent_color)

        palette = current_palette(app)
        muted = palette.text_muted if palette else "#646C7E"
        accent = palette.accent if palette else "#7C5CFF"

        self._collapse_button.setIcon(icon("menu", muted, 17))
        self._settings_button.setIcon(icon("settings", muted, 17))
        self._brand_icon_label.setPixmap(icon_pixmap("brand", accent, 18))
        self.search_box.set_icon_color(muted)
        self.sidebar.refresh_icons()

        for page in (self.home_page, self.favorites_page, self.history_page):
            if hasattr(page, "refresh"):
                page.refresh()
        for category in list(self._category_pages):
            self._refresh_category_page(category)

    def closeEvent(self, event) -> None:  # noqa: N802 (Qt override)
        self.context.shutdown()
        super().closeEvent(event)
