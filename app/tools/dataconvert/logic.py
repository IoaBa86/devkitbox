"""Pure JSON/YAML/CSV conversion logic — no Qt imports, fully unit-testable.

YAML parsing always uses ``yaml.safe_load`` (never plain ``yaml.load``) so a
pasted YAML document can't be used to construct arbitrary Python objects —
the default full loader is a known code-execution vector.
"""

from __future__ import annotations

import csv
import io
import json

import yaml

from app.core.exceptions import ValidationError

FORMATS = ("JSON", "YAML", "CSV")


def parse_json(text: str) -> object:
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidationError(
            f"Invalid JSON: {exc.msg}", line=exc.lineno, column=exc.colno
        ) from exc


def to_json(data: object) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


def parse_yaml(text: str) -> object:
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ValidationError(f"Invalid YAML: {exc}") from exc


def to_yaml(data: object) -> str:
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)


def parse_csv(text: str) -> list[dict[str, str]]:
    try:
        reader = csv.DictReader(io.StringIO(text))
        return [dict(row) for row in reader]
    except csv.Error as exc:
        raise ValidationError(f"Invalid CSV: {exc}") from exc


def to_csv(data: object) -> str:
    if not isinstance(data, list) or not all(isinstance(row, dict) for row in data):
        raise ValidationError("CSV output requires a list of flat objects")
    if not data:
        return ""

    fieldnames: list[str] = []
    for row in data:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in data:
        writer.writerow({k: ("" if v is None else v) for k, v in row.items()})
    return buffer.getvalue()


_PARSERS = {"JSON": parse_json, "YAML": parse_yaml, "CSV": parse_csv}
_SERIALIZERS = {"JSON": to_json, "YAML": to_yaml, "CSV": to_csv}


def convert(text: str, from_format: str, to_format: str) -> str:
    if from_format not in _PARSERS or to_format not in _SERIALIZERS:
        raise ValidationError(f"Unsupported format: {from_format} -> {to_format}")
    data = _PARSERS[from_format](text)
    return _SERIALIZERS[to_format](data)
