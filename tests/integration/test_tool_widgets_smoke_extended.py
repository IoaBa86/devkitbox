"""Widget-level smoke tests for the tools not covered by
test_tool_widgets_smoke.py — each primary action must run without raising
and produce the expected output, exercising widget + logic + services
together (this is exactly the layer that hid the Random Test Data table
row-height bug: logic-only unit tests never touch widget wiring)."""

from __future__ import annotations

from app.core.exceptions import ValidationError
from app.tools.api.logic import build_request
from app.tools.api.widget import ApiClientTool
from app.tools.case.widget import CaseConverterTool
from app.tools.fileinfo.widget import FileInformationTool
from app.tools.hash.widget import HashGeneratorTool
from app.tools.jwt.widget import JwtDecoderTool
from app.tools.lines.widget import LineToolsTool
from app.tools.markdown.widget import MarkdownPreviewTool
from app.tools.password.widget import PasswordGeneratorTool
from app.tools.regex.widget import RegexTesterTool
from app.tools.testdata.widget import RandomTestDataTool
from app.tools.text_stats.widget import TextStatisticsTool
from app.tools.textcompare.widget import TextCompareTool
from app.tools.url.widget import UrlTool
from app.tools.whitespace.widget import WhitespaceCleanerTool


def test_jwt_decoder_widget_decodes(qtbot, context):
    widget = JwtDecoderTool(context)
    qtbot.addWidget(widget)

    token = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIn0."
        "dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
    )
    widget._input.setPlainText(token)
    widget._decode(announce=True)

    assert '"sub"' in widget._payload_view.toPlainText()
    assert widget._status_label.text() == ""


def test_jwt_decoder_widget_rejects_malformed_token(qtbot, context):
    widget = JwtDecoderTool(context)
    qtbot.addWidget(widget)

    widget._input.setPlainText("not-a-jwt")
    widget._decode(announce=True)  # must not raise

    assert widget._payload_view.toPlainText() == ""
    assert widget._status_label.text() != ""


def test_hash_generator_widget_hashes_text(qtbot, context):
    widget = HashGeneratorTool(context)
    qtbot.addWidget(widget)

    widget._algo_checks["MD5"].setChecked(False)
    widget._algo_checks["SHA-256"].setChecked(True)
    widget._input.setPlainText("hello")
    widget._hash_text()

    assert widget._table.rowCount() == 1
    assert widget._table.item(0, 0).text() == "SHA-256"
    assert len(widget._table.item(0, 1).text()) == 64


def test_regex_tester_widget_finds_matches(qtbot, context):
    widget = RegexTesterTool(context)
    qtbot.addWidget(widget)

    widget._pattern_edit.setText(r"\d+")
    widget._text_edit.setPlainText("a1 b22 c333")

    assert widget._table.rowCount() == 3
    assert "3 matches" in widget._status_label.text()


def test_regex_tester_widget_handles_invalid_pattern(qtbot, context):
    widget = RegexTesterTool(context)
    qtbot.addWidget(widget)

    widget._pattern_edit.setText("(")  # invalid regex, must not raise

    assert widget._table.rowCount() == 0


def test_regex_tester_widget_shows_timeout_message(qtbot, context, monkeypatch):
    from app.tools.regex.logic import RegexTimeoutError

    def _raise_timeout(*args, **kwargs):
        raise RegexTimeoutError("Pattern is taking too long (possible catastrophic backtracking)")

    monkeypatch.setattr("app.tools.regex.widget.find_matches", _raise_timeout)

    widget = RegexTesterTool(context)
    qtbot.addWidget(widget)

    widget._pattern_edit.setText(r"(a+)+$")
    widget._text_edit.setPlainText("a" * 40 + "!")

    assert "taking too long" in widget._status_label.text()
    assert widget._table.rowCount() == 0


def test_url_tool_widget_encode_decode_roundtrip(qtbot, context):
    widget = UrlTool(context)
    qtbot.addWidget(widget)

    widget._input.setPlainText("hello world/?")
    widget._encode()
    encoded = widget._output.toPlainText()
    assert encoded

    widget._input.setPlainText(encoded)
    widget._decode()
    assert widget._output.toPlainText() == "hello world/?"


def test_url_tool_widget_parses_query_string(qtbot, context):
    widget = UrlTool(context)
    qtbot.addWidget(widget)

    widget._query_edit.setText("https://example.com/search?page=2&sort=newest")
    widget._parse_query()

    assert widget._params_table.rowCount() == 2
    assert widget._params_table.item(0, 0).text() == "page"


def test_password_generator_widget_generates_password(qtbot, context):
    widget = PasswordGeneratorTool(context)
    qtbot.addWidget(widget)

    widget._length_spin.setValue(20)
    widget._generate()

    assert len(widget._output.text()) == 20
    assert "Strength" in widget._strength_label.text()


def test_password_generator_widget_generates_passphrase(qtbot, context):
    widget = PasswordGeneratorTool(context)
    qtbot.addWidget(widget)

    widget._passphrase_radio.setChecked(True)
    widget._word_count_spin.setValue(5)
    widget._generate()

    assert len(widget._output.text().split("-")) == 5


def test_case_converter_widget_updates_live(qtbot, context):
    widget = CaseConverterTool(context)
    qtbot.addWidget(widget)

    widget._input.setPlainText("hello world")

    names = [widget._table.item(row, 0).text() for row in range(widget._table.rowCount())]
    snake_row = names.index("snake_case")
    assert widget._table.item(snake_row, 1).text() == "hello_world"


def test_line_tools_widget_sorts(qtbot, context):
    widget = LineToolsTool(context)
    qtbot.addWidget(widget)

    widget._input.setPlainText("banana\napple\ncherry")
    widget._run(__import__("app.tools.lines.logic", fromlist=["sort_ascending"]).sort_ascending)

    assert widget._output.toPlainText() == "apple\nbanana\ncherry"


def test_text_statistics_widget_updates_live(qtbot, context):
    widget = TextStatisticsTool(context)
    qtbot.addWidget(widget)

    widget._input.setPlainText("hello world")

    assert widget._words_label.text() == "2"


def test_whitespace_cleaner_widget_cleans(qtbot, context):
    widget = WhitespaceCleanerTool(context)
    qtbot.addWidget(widget)

    widget._input.setPlainText("a  \nb\t")
    from app.tools.whitespace.logic import trim_trailing_whitespace

    widget._run(trim_trailing_whitespace)

    assert widget._output.toPlainText() == "a\nb"


def test_file_information_widget_inspects_file(qtbot, context, tmp_path, monkeypatch):
    widget = FileInformationTool(context)
    qtbot.addWidget(widget)

    sample = tmp_path / "sample.txt"
    sample.write_bytes(b"hello world")

    monkeypatch.setattr(
        "app.tools.fileinfo.widget.QFileDialog.getOpenFileName",
        lambda *args, **kwargs: (str(sample), ""),
    )
    widget._select_file()

    assert widget._table.item(0, 1).text() == "sample.txt"
    assert widget._info is not None


def test_text_compare_widget_computes_diff(qtbot, context):
    widget = TextCompareTool(context)
    qtbot.addWidget(widget)

    widget._left.setPlainText("a\nb\nc")
    widget._right.setPlainText("a\nx\nc")
    widget._compare()

    assert "- b" in widget._output.toPlainText()
    assert "+ x" in widget._output.toPlainText()
    assert "Similarity" in widget._stats_label.text()


def test_markdown_preview_widget_renders_live(qtbot, context):
    widget = MarkdownPreviewTool(context)
    qtbot.addWidget(widget)

    widget._input.setPlainText("# Title\n\nSome text.")

    assert "4 words" in widget._stats_label.text()
    assert "1 headings" in widget._stats_label.text()


def test_random_test_data_widget_generates_json(qtbot, context):
    widget = RandomTestDataTool(context)
    qtbot.addWidget(widget)

    widget._count_spin.setValue(3)
    widget._generate()

    import json

    records = json.loads(widget._output.toPlainText())
    assert len(records) == 3
    assert "id" in records[0]


def test_random_test_data_widget_field_rows_are_visible_height(qtbot, context):
    widget = RandomTestDataTool(context)
    qtbot.addWidget(widget)

    # Regression guard for the row-clipping bug: a row must be at least as
    # tall as its embedded QLineEdit/QComboBox wants to be, or the widget's
    # text renders clipped inside the row.
    for row in range(widget._field_table.rowCount()):
        cell_widget = widget._field_table.cellWidget(row, 0)
        assert widget._field_table.rowHeight(row) >= cell_widget.sizeHint().height()


def test_api_client_widget_rejects_invalid_url(qtbot, context):
    widget = ApiClientTool(context)
    qtbot.addWidget(widget)

    widget._url_edit.setText("not-a-url")
    widget._send()  # must not raise, must not start a network thread

    assert widget._thread is None


def test_api_client_build_request_used_by_widget_matches_logic():
    request = build_request("GET", "https://example.com", {}, "")
    assert request.method == "GET"
    try:
        build_request("GET", "bad-url", {}, "")
        raised = False
    except ValidationError:
        raised = True
    assert raised
