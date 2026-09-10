"""Application-wide constants. Single source of truth for identity/versioning."""

APP_NAME = "DevKitBox"
APP_DISPLAY_NAME = "DevKitBox"
APP_TAGLINE = "Your Developer Toolbox for Windows"
APP_VERSION = "1.0.0"
ORG_NAME = "DevKitBox"
WEBSITE_URL = "https://devkitbox.net"

# No public repository exists yet. Do not invent one — leave unset until real.
GITHUB_URL: str | None = None

DB_FILENAME = "devkitbox.sqlite3"
LOG_FILENAME = "devkitbox.log"

DEFAULT_WINDOW_WIDTH = 1280
DEFAULT_WINDOW_HEIGHT = 800
DEFAULT_SIDEBAR_WIDTH = 220
COLLAPSED_SIDEBAR_WIDTH = 56

TOOL_CATEGORIES = ["Development", "Encoding", "Text", "Generators", "Files", "Network", "Design"]
