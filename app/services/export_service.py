"""File read/write helpers shared by tools that load or save content."""

from __future__ import annotations

from pathlib import Path

from app.core.exceptions import FileOperationError


class ExportService:
    def save_text(self, path: str | Path, content: str) -> None:
        try:
            Path(path).write_text(content, encoding="utf-8")
        except OSError as exc:
            raise FileOperationError(f"Could not save file: {path}", detail=str(exc)) from exc

    def load_text(self, path: str | Path) -> str:
        try:
            return Path(path).read_text(encoding="utf-8")
        except OSError as exc:
            raise FileOperationError(f"Could not read file: {path}", detail=str(exc)) from exc

    def save_bytes(self, path: str | Path, content: bytes) -> None:
        try:
            Path(path).write_bytes(content)
        except OSError as exc:
            raise FileOperationError(f"Could not save file: {path}", detail=str(exc)) from exc

    def load_bytes(self, path: str | Path) -> bytes:
        try:
            return Path(path).read_bytes()
        except OSError as exc:
            raise FileOperationError(f"Could not read file: {path}", detail=str(exc)) from exc
