from __future__ import annotations

from app.ui.widgets.command_palette import CommandPalette, PaletteCommand


def test_palette_lists_tools_when_query_empty(qtbot, context):
    palette = CommandPalette(context, [], lambda _tid: None)
    qtbot.addWidget(palette)

    assert palette._list.count() == len(context.tool_registry.get_all())


def test_palette_filters_by_query(qtbot, context):
    palette = CommandPalette(context, [], lambda _tid: None)
    qtbot.addWidget(palette)

    palette._input.setText("json")

    labels = [cmd.label for cmd in palette._commands]
    assert "JSON Formatter" in labels
    assert "Base64" not in labels


def test_palette_includes_matching_static_commands(qtbot, context):
    commands = [PaletteCommand("Go to Settings", "Navigation", lambda: None)]
    palette = CommandPalette(context, commands, lambda _tid: None)
    qtbot.addWidget(palette)

    palette._input.setText("settings")

    labels = [cmd.label for cmd in palette._commands]
    assert "Go to Settings" in labels


def test_palette_activating_tool_command_calls_open_tool(qtbot, context):
    opened: list[str] = []
    palette = CommandPalette(context, [], opened.append)
    qtbot.addWidget(palette)

    palette._input.setText("json")
    palette._activate_current()

    assert opened == ["json_formatter"]
