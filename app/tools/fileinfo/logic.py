"""Pure file-information logic — no Qt imports, fully unit-testable."""

from __future__ import annotations

import datetime
import hashlib
import mimetypes
from dataclasses import dataclass
from pathlib import Path

from app.core.exceptions import FileOperationError

_CHUNK_SIZE = 1024 * 1024
_SIZE_UNITS = ("B", "KB", "MB", "GB", "TB")


@dataclass(frozen=True, slots=True)
class FileInfo:
    name: str
    path: str
    size_bytes: int
    mime_type: str
    extension: str
    created: datetime.datetime
    modified: datetime.datetime
    md5: str
    sha256: str


def format_size(size_bytes: int) -> str:
    size = float(size_bytes)
    for unit in _SIZE_UNITS:
        if size < 1024 or unit == _SIZE_UNITS[-1]:
            return f"{size:.2f} {unit}" if unit != "B" else f"{int(size)} {unit}"
        size /= 1024
    return f"{size:.2f} {_SIZE_UNITS[-1]}"


def _hash_file(path: Path) -> tuple[str, str]:
    md5 = hashlib.md5()
    sha256 = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(_CHUNK_SIZE)
            if not chunk:
                break
            md5.update(chunk)
            sha256.update(chunk)
    return md5.hexdigest(), sha256.hexdigest()


def inspect_file(path: str | Path) -> FileInfo:
    file_path = Path(path)
    if not file_path.exists():
        raise FileOperationError(f"File not found: {path}")
    if not file_path.is_file():
        raise FileOperationError(f"Not a file: {path}")

    try:
        stat = file_path.stat()
        md5, sha256 = _hash_file(file_path)
    except OSError as exc:
        raise FileOperationError(f"Could not read file: {path}", detail=str(exc)) from exc

    mime_type, _ = mimetypes.guess_type(file_path.name)

    return FileInfo(
        name=file_path.name,
        path=str(file_path.resolve()),
        size_bytes=stat.st_size,
        mime_type=mime_type or "application/octet-stream",
        extension=file_path.suffix,
        created=datetime.datetime.fromtimestamp(stat.st_ctime, tz=datetime.UTC),
        modified=datetime.datetime.fromtimestamp(stat.st_mtime, tz=datetime.UTC),
        md5=md5,
        sha256=sha256,
    )
