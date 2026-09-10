from __future__ import annotations

import json

import pytest

from app.tools.testdata.logic import FieldSpec, generate_records, to_csv, to_json


def test_generate_records_count_and_fields():
    fields = [FieldSpec("name", "Full Name"), FieldSpec("email", "Email")]
    records = generate_records(fields, 5)
    assert len(records) == 5
    for record in records:
        assert set(record.keys()) == {"name", "email"}
        assert "@" in record["email"]


def test_generate_records_zero_count():
    assert generate_records([FieldSpec("id", "UUID")], 0) == []


def test_generate_records_negative_count_raises():
    with pytest.raises(ValueError):
        generate_records([FieldSpec("id", "UUID")], -1)


def test_generate_records_unknown_type_raises():
    with pytest.raises(ValueError):
        generate_records([FieldSpec("x", "NotAType")], 1)


def test_generate_records_boolean_type():
    records = generate_records([FieldSpec("flag", "Boolean")], 20)
    assert all(isinstance(r["flag"], bool) for r in records)


def test_generate_records_integer_and_float_types():
    records = generate_records([FieldSpec("i", "Integer"), FieldSpec("f", "Float")], 10)
    assert all(isinstance(r["i"], int) for r in records)
    assert all(isinstance(r["f"], float) for r in records)


def test_to_json_round_trips():
    records = generate_records([FieldSpec("name", "Full Name")], 3)
    parsed = json.loads(to_json(records))
    assert parsed == records


def test_to_csv_has_header_and_rows():
    records = generate_records([FieldSpec("name", "Full Name")], 2)
    csv_text = to_csv(records, ["name"])
    lines = csv_text.strip().splitlines()
    assert lines[0] == "name"
    assert len(lines) == 3
