from __future__ import annotations

import hashlib

import pytest

from app.core.exceptions import FileOperationError
from app.tools.fileinfo.logic import format_size, inspect_file


def test_format_size_bytes():
    assert format_size(500) == "500 B"


def test_format_size_kilobytes():
    assert format_size(2048) == "2.00 KB"


def test_format_size_megabytes():
    assert format_size(5 * 1024 * 1024) == "5.00 MB"


def test_inspect_file_not_found(tmp_path):
    missing = tmp_path / "missing.txt"
    with pytest.raises(FileOperationError):
        inspect_file(missing)


def test_inspect_file_directory_raises(tmp_path):
    with pytest.raises(FileOperationError):
        inspect_file(tmp_path)


def test_inspect_file_basic_fields(tmp_path):
    file_path = tmp_path / "sample.txt"
    content = b"hello world"
    file_path.write_bytes(content)

    info = inspect_file(file_path)

    assert info.name == "sample.txt"
    assert info.extension == ".txt"
    assert info.size_bytes == len(content)
    assert info.mime_type == "text/plain"
    assert info.md5 == hashlib.md5(content).hexdigest()
    assert info.sha256 == hashlib.sha256(content).hexdigest()
