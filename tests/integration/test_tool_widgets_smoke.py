"""End-to-end smoke tests: each tool widget must construct and its primary
action must run without raising, exercising widget + logic + services together."""

from __future__ import annotations

from app.tools.base64.widget import Base64Tool
from app.tools.json.widget import JsonFormatterTool
from app.tools.timestamp.widget import TimestampConverterTool
from app.tools.uuid.widget import UuidGeneratorTool


def test_json_formatter_widget_formats(qtbot, context):
    widget = JsonFormatterTool(context)
    qtbot.addWidget(widget)

    widget._input.setPlainText('{"b":1,"a":2}')
    widget._format()

    assert widget._output.toPlainText() == '{\n  "b": 1,\n  "a": 2\n}'


def test_json_formatter_widget_handles_invalid_input(qtbot, context):
    widget = JsonFormatterTool(context)
    qtbot.addWidget(widget)

    widget._input.setPlainText("{not json")
    widget._format()  # must not raise

    assert widget._output.toPlainText() == ""
    assert "Invalid JSON" in widget._status_label.text()


def test_base64_widget_roundtrip(qtbot, context):
    widget = Base64Tool(context)
    qtbot.addWidget(widget)

    widget._input.setPlainText("hello world")
    widget._encode()
    encoded = widget._output.toPlainText()
    assert encoded

    widget._input.setPlainText(encoded)
    widget._decode()
    assert widget._output.toPlainText() == "hello world"


def test_uuid_generator_widget_generates(qtbot, context):
    widget = UuidGeneratorTool(context)
    qtbot.addWidget(widget)

    widget._generate()
    lines = widget._output.toPlainText().splitlines()
    assert len(lines) == 1
    assert len(lines[0]) == 36


def test_timestamp_widget_shows_current_on_init(qtbot, context):
    widget = TimestampConverterTool(context)
    qtbot.addWidget(widget)

    assert widget._unix_seconds_edit.text() != ""


def test_timestamp_widget_converts_unix_seconds(qtbot, context):
    widget = TimestampConverterTool(context)
    qtbot.addWidget(widget)

    widget._format_combo.setCurrentText("Unix seconds")
    widget._input_edit.setText("1704110400")
    widget._convert()

    assert widget._utc_edit.text() == "2024-01-01 12:00:00 UTC"


def test_favoriting_a_tool_persists(qtbot, context):
    widget = JsonFormatterTool(context)
    qtbot.addWidget(widget)

    assert context.history_service.is_favorite("json_formatter") is False
    widget._on_favorite_clicked()
    assert context.history_service.is_favorite("json_formatter") is True
