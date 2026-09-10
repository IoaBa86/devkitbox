# Architecture

DevKitBox is a PySide6 (Qt) desktop app structured in four layers, each with
a single responsibility:

```
app/core      startup, paths, logging, config, exceptions
app/models    plain data models (settings, tool metadata) — no Qt, no I/O
app/services  SQLite access, settings, favorites/history, clipboard, export
app/ui        the Qt shell: main window, theme, widgets, pages
app/tools     the tool registry and every individual tool
```

## Startup order

`app/main.py` wires everything together in this order:

1. `app.core.paths.ensure_dirs()` — create the per-user data directory
2. `app.core.logging.setup_logging()`
3. `AppContext` — constructs the database connection, runs migrations,
   loads settings, and builds the shared services (clipboard, export,
   history, tool registry)
4. `_register_tools(context)` — imports every tool's `widget.py` and
   registers its class with the tool registry
5. `MainWindow(context)` — builds the shell (sidebar, home page, settings,
   etc.) and shows it

`AppContext` (`app/core/app_context.py`) is the one object threaded through
the whole app — every page and every tool widget receives it and reaches
services through it rather than constructing their own.

## The tool registry

`app/tools/registry.py` holds a `dict[str, type[ToolWidget]]` keyed by tool
id. The shell (`app/ui/main_window.py`, `app/ui/pages/home_page.py`,
`app/ui/widgets/sidebar.py`, the command palette) never hard-codes a list of
tools — it always asks the registry (`get_all()`, `get_by_category()`,
`search()`). This is what lets `_register_tools()` be the *only* place that
knows the full tool list.

## Anatomy of a tool

Every tool lives at `app/tools/<name>/` with two files:

- **`logic.py`** — pure functions and dataclasses. No Qt imports, no I/O
  beyond what the function explicitly does (e.g. `fileinfo/logic.py`
  reading a file the user picked). This is what unit tests exercise
  directly, and it's what makes every tool's actual behavior verifiable
  without spinning up a GUI.
- **`widget.py`** — a `ToolWidget` subclass (see `app/tools/base.py`) that
  wires Qt controls to the logic functions. It declares a module-level
  `METADATA = ToolMetadata(id=..., name=..., description=..., category=...,
  keywords=...)` and implements `build_content()` (required) and
  `build_actions()` (optional — the action bar under the content).

`ToolWidget` handles everything every tool page needs regardless of what it
does: the header (category eyebrow, title, description, favorite star), the
content area, and the action bar. A new tool only implements the two
methods above — it never touches header/favorite/layout plumbing.

To add a new tool:

1. Create `app/tools/<name>/logic.py` and `widget.py` (see any existing
   tool, e.g. `app/tools/base64/`, for the pattern).
2. Register it in `app/main.py::_register_tools()` — import the widget
   class and add it to the registration tuple.
3. If it introduces a new category, add the category name to
   `TOOL_CATEGORIES` in `app/core/constants.py` and a matching entry in
   `CATEGORY_ICON` in `app/ui/icons.py`.
4. Write `tests/unit/test_<name>_logic.py` for the logic module, and add a
   widget smoke test in `tests/integration/` exercising the real button/
   signal wiring — logic-only tests can't catch layout or wiring bugs
   (this project has hit both: a table row too short to show its own
   text, and a mode toggle that hid a value label but not its field-name
   label).

## Settings and persistence

`app/models/settings.py::AppSettings` is a plain dataclass; every field also
has an entry in `SETTINGS_FIELD_TYPES` so `SettingsService` (backed by a
`key`/`value` SQLite table) can round-trip it. Nothing reads or writes
settings directly from SQLite outside that service.

## Frozen builds

`app/core/paths.py::get_resource_root()` is the one thing in the codebase
that has to know it might be running from a PyInstaller bundle rather than
from source — it resolves to `sys._MEIPASS` (or the executable's directory)
when `sys.frozen` is set, and to the project root otherwise. Anything that
needs a bundled, read-only resource (currently just `assets/`) should go
through this rather than a source-relative `Path(__file__)` walk, which
breaks once frozen.

See [`installer/devkitbox.spec`](../installer/devkitbox.spec) and
[`installer/devkitbox.iss`](../installer/devkitbox.iss) for the actual
packaging configuration, and the README's "Building the installer" section
for the build commands.
