"""Pure hashing logic — no Qt imports, fully unit-testable.

File hashing accepts an optional progress callback so the widget can drive
a QThread worker without this module depending on Qt.
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from pathlib import Path

from app.core.exceptions import FileOperationError

ALGORITHMS: dict[str, Callable[[], hashlib._Hash]] = {
    "MD5": hashlib.md5,
    "SHA-1": hashlib.sha1,
    "SHA-224": hashlib.sha224,
    "SHA-256": hashlib.sha256,
    "SHA-384": hashlib.sha384,
    "SHA-512": hashlib.sha512,
}

_CHUNK_SIZE = 1024 * 1024


def hash_text(text: str, algorithms: list[str]) -> dict[str, str]:
    data = text.encode("utf-8")
    return {name: ALGORITHMS[name](data).hexdigest() for name in algorithms}


def hash_file(
    path: str | Path,
    algorithms: list[str],
    progress_cb: Callable[[int, int], None] | None = None,
) -> dict[str, str]:
    hashers = {name: ALGORITHMS[name]() for name in algorithms}
    file_path = Path(path)
    total = file_path.stat().st_size if file_path.exists() else 0
    read_bytes = 0

    try:
        with file_path.open("rb") as handle:
            while True:
                chunk = handle.read(_CHUNK_SIZE)
                if not chunk:
                    break
                for hasher in hashers.values():
                    hasher.update(chunk)
                read_bytes += len(chunk)
                if progress_cb:
                    progress_cb(read_bytes, total)
    except OSError as exc:
        raise FileOperationError(f"Could not read file: {path}", detail=str(exc)) from exc

    return {name: hasher.hexdigest() for name, hasher in hashers.items()}
