from __future__ import annotations

import pytest

from app.core.exceptions import ValidationError
from app.tools.dataconvert.logic import convert, parse_csv, parse_json, parse_yaml, to_csv, to_yaml


def test_parse_json_valid():
    assert parse_json('{"a": 1}') == {"a": 1}


def test_parse_json_invalid_raises():
    with pytest.raises(ValidationError):
        parse_json("{not json")


def test_parse_yaml_valid():
    assert parse_yaml("a: 1\nb: 2\n") == {"a": 1, "b": 2}


def test_parse_yaml_invalid_raises():
    with pytest.raises(ValidationError):
        parse_yaml("a: [unclosed")


def test_parse_yaml_never_executes_arbitrary_tags():
    # yaml.safe_load must refuse Python-object tags rather than instantiate them.
    with pytest.raises(ValidationError):
        parse_yaml("!!python/object/apply:os.system ['echo pwned']")


def test_parse_csv_basic():
    result = parse_csv("name,age\nAlice,30\nBob,25\n")
    assert result == [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]


def test_to_csv_from_list_of_dicts():
    csv_text = to_csv([{"name": "Alice", "age": 30}])
    assert csv_text == "name,age\r\nAlice,30\r\n"


def test_to_csv_empty_list():
    assert to_csv([]) == ""


def test_to_csv_rejects_non_flat_data():
    with pytest.raises(ValidationError):
        to_csv({"not": "a list"})


def test_to_yaml_round_trip():
    data = {"a": 1, "b": [1, 2, 3]}
    yaml_text = to_yaml(data)
    assert parse_yaml(yaml_text) == data


def test_convert_json_to_yaml():
    result = convert('{"a": 1}', "JSON", "YAML")
    assert result.strip() == "a: 1"


def test_convert_yaml_to_json():
    result = convert("a: 1\nb: 2\n", "YAML", "JSON")
    assert parse_json(result) == {"a": 1, "b": 2}


def test_convert_csv_to_json():
    result = convert("name,age\nAlice,30\n", "CSV", "JSON")
    assert parse_json(result) == [{"name": "Alice", "age": "30"}]


def test_convert_json_to_csv():
    result = convert('[{"name": "Alice", "age": 30}]', "JSON", "CSV")
    assert result == "name,age\r\nAlice,30\r\n"


def test_convert_unsupported_format_raises():
    with pytest.raises(ValidationError):
        convert("{}", "JSON", "XML")
