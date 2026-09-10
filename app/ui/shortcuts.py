"""Central definition of global keyboard shortcuts.

Kept as plain key-sequence strings (rather than QShortcut objects) so both
the main window and the command palette can reference the same source of
truth without importing widgets into each other.
"""

from __future__ import annotations

COMMAND_PALETTE = "Ctrl+K"
OPEN_SETTINGS = "Ctrl+,"
FOCUS_SEARCH = "Ctrl+Shift+F"
SAVE = "Ctrl+S"
COPY_RESULT = "Ctrl+Shift+C"
PRIMARY_ACTION = "Ctrl+Return"
CLOSE_OVERLAY = "Esc"
