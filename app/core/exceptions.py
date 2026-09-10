"""Application exception hierarchy.

All exceptions carry a human-readable ``message`` intended for direct display
in the UI, plus optional structured detail (line/column, path, etc.) that
callers can use to build more contextual messages.
"""

from __future__ import annotations


class DevKitBoxError(Exception):
    """Base class for all application-raised errors."""

    def __init__(self, message: str, *, detail: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.detail = detail


class ValidationError(DevKitBoxError):
    """Raised when user-supplied input fails validation (bad JSON, regex, etc.)."""

    def __init__(
        self,
        message: str,
        *,
        line: int | None = None,
        column: int | None = None,
        detail: str | None = None,
    ) -> None:
        super().__init__(message, detail=detail)
        self.line = line
        self.column = column


class FileOperationError(DevKitBoxError):
    """Raised on file read/write/permission failures."""


class DatabaseError(DevKitBoxError):
    """Raised on SQLite initialization, migration, or query failures."""


class NetworkError(DevKitBoxError):
    """Raised on HTTP request failures (timeout, connection, malformed response)."""
