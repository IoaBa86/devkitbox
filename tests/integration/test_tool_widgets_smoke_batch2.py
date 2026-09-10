"""Widget-level smoke tests for the tools added after the first two smoke
batches — each primary action must run without raising and produce the
expected output, exercising widget + logic + services together."""

from __future__ import annotations

from app.tools.certdecoder.widget import CertificateDecoderTool
from app.tools.color.widget import ColorTool
from app.tools.cookieparser.widget import CookieParserTool
from app.tools.cron.widget import CronExplainerTool
from app.tools.dataconvert.widget import DataConverterTool
from app.tools.envparser.widget import EnvParserTool
from app.tools.htmlentities.widget import HtmlEntitiesTool
from app.tools.imagebase64.widget import ImageBase64Tool
from app.tools.ipcalc.widget import IpSubnetCalculatorTool
from app.tools.jwt.encoder_widget import JwtEncoderTool
from app.tools.loremipsum.widget import LoremIpsumGeneratorTool
from app.tools.numberbase.widget import NumberBaseConverterTool
from app.tools.qrcode.widget import QrCodeGeneratorTool
from app.tools.sqlformat.widget import SqlFormatterTool
from app.tools.timezone.widget import TimezoneConverterTool
from app.tools.unitconvert.widget import UnitConverterTool
from app.tools.useragent.widget import UserAgentParserTool
from app.tools.xml.widget import XmlFormatterTool


def test_color_widget_updates_live(qtbot, context):
    widget = ColorTool(context)
    qtbot.addWidget(widget)

    widget._hex_edit.setText("#ff0000")

    assert widget._rgb_label.text() == "rgb(255, 0, 0)"


def test_certificate_decoder_widget_rejects_invalid_pem(qtbot, context):
    widget = CertificateDecoderTool(context)
    qtbot.addWidget(widget)

    widget._input.setPlainText("not a certificate")
    widget._decode()  # must not raise

    assert widget._labels["Subject"].text() == "—"


def test_cron_widget_updates_live(qtbot, context):
    widget = CronExplainerTool(context)
    qtbot.addWidget(widget)

    widget._expression_edit.setText("0 9 * * *")

    assert widget._description_label.text() == "At 09:00"
    assert widget._runs_list.count() == 10


def test_dataconvert_widget_converts(qtbot, context):
    widget = DataConverterTool(context)
    qtbot.addWidget(widget)

    widget._input.setPlainText('{"a": 1}')
    widget._from_combo.setCurrentText("JSON")
    widget._to_combo.setCurrentText("YAML")
    widget._convert()

    assert widget._output.toPlainText().strip() == "a: 1"


def test_envparser_widget_parses(qtbot, context):
    widget = EnvParserTool(context)
    qtbot.addWidget(widget)

    widget._input.setPlainText("FOO=bar")
    widget._parse()

    assert widget._table.rowCount() == 1
    assert widget._table.item(0, 0).text() == "FOO"


def test_cookieparser_widget_parses_set_cookie(qtbot, context):
    widget = CookieParserTool(context)
    qtbot.addWidget(widget)

    widget._input.setText("session_id=abc123; Secure")
    widget._parse()

    assert widget._labels["Name"].text() == "session_id"
    assert widget._labels["Secure"].text() == "Yes"


def test_htmlentities_widget_encodes(qtbot, context):
    widget = HtmlEntitiesTool(context)
    qtbot.addWidget(widget)

    widget._input.setPlainText("Tom & Jerry")
    widget._encode()

    assert widget._output.toPlainText() == "Tom &amp; Jerry"


def test_imagebase64_widget_rejects_invalid_base64(qtbot, context):
    widget = ImageBase64Tool(context)
    qtbot.addWidget(widget)

    widget._input.setPlainText("not valid base64!!!")
    widget._preview()  # must not raise

    assert widget._preview_label.text() == "No image"


def test_ipcalc_widget_updates_live(qtbot, context):
    widget = IpSubnetCalculatorTool(context)
    qtbot.addWidget(widget)

    widget._input.setText("10.0.0.0/8")

    assert widget._labels["Network Address"].text() == "10.0.0.0"


def test_jwt_encoder_widget_generates(qtbot, context):
    widget = JwtEncoderTool(context)
    qtbot.addWidget(widget)

    widget._generate()

    assert len(widget._output.toPlainText().split(".")) == 3


def test_loremipsum_widget_generates_on_init(qtbot, context):
    widget = LoremIpsumGeneratorTool(context)
    qtbot.addWidget(widget)

    assert widget._output.toPlainText() != ""


def test_numberbase_widget_updates_live(qtbot, context):
    widget = NumberBaseConverterTool(context)
    qtbot.addWidget(widget)

    widget._from_combo.setCurrentText("Decimal")
    widget._value_edit.setText("42")

    assert widget._result_labels["Binary"].text() == "101010"
    assert widget._result_labels["Hexadecimal"].text() == "2a"


def test_qrcode_widget_generates(qtbot, context):
    widget = QrCodeGeneratorTool(context)
    qtbot.addWidget(widget)

    widget._input.setPlainText("https://devkitbox.net")
    widget._generate()

    assert widget._pixmap is not None


def test_sqlformat_widget_formats(qtbot, context):
    widget = SqlFormatterTool(context)
    qtbot.addWidget(widget)

    widget._input.setPlainText("select 1")
    widget._format()

    assert "SELECT" in widget._output.toPlainText()


def test_timezone_widget_populates_on_init(qtbot, context):
    widget = TimezoneConverterTool(context)
    qtbot.addWidget(widget)

    assert widget._table.rowCount() > 0


def test_unitconvert_widget_populates_on_init(qtbot, context):
    widget = UnitConverterTool(context)
    qtbot.addWidget(widget)

    assert widget._table.rowCount() > 0


def test_useragent_widget_updates_live(qtbot, context):
    widget = UserAgentParserTool(context)
    qtbot.addWidget(widget)

    widget._input.setPlainText(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/128.0.0.0 Safari/537.36"
    )

    assert widget._labels["Browser"].text() == "Chrome 128.0.0.0"


def test_xml_widget_formats(qtbot, context):
    widget = XmlFormatterTool(context)
    qtbot.addWidget(widget)

    widget._input.setPlainText("<root><child>value</child></root>")
    widget._format()

    assert "<root>" in widget._output.toPlainText()
