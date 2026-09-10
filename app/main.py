"""DevKitBox entry point.

Startup order: paths -> logging -> database/migrations -> settings ->
tool registry -> UI -> theme -> show window.
"""

from __future__ import annotations

import sys
import traceback

from PySide6.QtWidgets import QApplication, QMessageBox

from app.core.app_context import AppContext
from app.core.constants import APP_NAME
from app.core.exceptions import DevKitBoxError
from app.core.logging import get_logger, setup_logging
from app.core.paths import ensure_dirs
from app.ui.main_window import MainWindow


def _install_exception_hook(logger) -> None:
    def handle(exc_type, exc_value, exc_tb) -> None:
        logger.error(
            "Unhandled exception: %s",
            "".join(traceback.format_exception(exc_type, exc_value, exc_tb)),
        )
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return
        QMessageBox.critical(
            None,
            APP_NAME,
            f"An unexpected error occurred:\n\n{exc_value}",
        )

    sys.excepthook = handle


def main() -> int:
    ensure_dirs()
    logger = setup_logging()
    _install_exception_hook(logger)

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(APP_NAME)

    try:
        context = AppContext(logger)
    except DevKitBoxError as exc:
        QMessageBox.critical(None, APP_NAME, exc.message)
        return 1

    _register_tools(context)

    window = MainWindow(context)
    window.show()

    exit_code = app.exec()
    return exit_code


def _register_tools(context: AppContext) -> None:
    """Import and register tool implementations. Populated milestone by milestone."""
    from app.tools.api.widget import ApiClientTool
    from app.tools.base64.widget import Base64Tool
    from app.tools.case.widget import CaseConverterTool
    from app.tools.certdecoder.widget import CertificateDecoderTool
    from app.tools.color.widget import ColorTool
    from app.tools.cookieparser.widget import CookieParserTool
    from app.tools.cron.widget import CronExplainerTool
    from app.tools.dataconvert.widget import DataConverterTool
    from app.tools.envparser.widget import EnvParserTool
    from app.tools.fileinfo.widget import FileInformationTool
    from app.tools.hash.widget import HashGeneratorTool
    from app.tools.htmlentities.widget import HtmlEntitiesTool
    from app.tools.imagebase64.widget import ImageBase64Tool
    from app.tools.ipcalc.widget import IpSubnetCalculatorTool
    from app.tools.json.widget import JsonFormatterTool
    from app.tools.jwt.encoder_widget import JwtEncoderTool
    from app.tools.jwt.widget import JwtDecoderTool
    from app.tools.lines.widget import LineToolsTool
    from app.tools.loremipsum.widget import LoremIpsumGeneratorTool
    from app.tools.markdown.widget import MarkdownPreviewTool
    from app.tools.numberbase.widget import NumberBaseConverterTool
    from app.tools.password.widget import PasswordGeneratorTool
    from app.tools.qrcode.widget import QrCodeGeneratorTool
    from app.tools.regex.widget import RegexTesterTool
    from app.tools.sqlformat.widget import SqlFormatterTool
    from app.tools.testdata.widget import RandomTestDataTool
    from app.tools.text_stats.widget import TextStatisticsTool
    from app.tools.textcompare.widget import TextCompareTool
    from app.tools.timestamp.widget import TimestampConverterTool
    from app.tools.timezone.widget import TimezoneConverterTool
    from app.tools.unitconvert.widget import UnitConverterTool
    from app.tools.url.widget import UrlTool
    from app.tools.useragent.widget import UserAgentParserTool
    from app.tools.uuid.widget import UuidGeneratorTool
    from app.tools.whitespace.widget import WhitespaceCleanerTool
    from app.tools.xml.widget import XmlFormatterTool

    for tool_cls in (
        JsonFormatterTool,
        Base64Tool,
        UuidGeneratorTool,
        TimestampConverterTool,
        JwtDecoderTool,
        HashGeneratorTool,
        RegexTesterTool,
        UrlTool,
        PasswordGeneratorTool,
        CaseConverterTool,
        LineToolsTool,
        TextStatisticsTool,
        WhitespaceCleanerTool,
        FileInformationTool,
        TextCompareTool,
        MarkdownPreviewTool,
        RandomTestDataTool,
        ApiClientTool,
        ColorTool,
        NumberBaseConverterTool,
        DataConverterTool,
        CronExplainerTool,
        XmlFormatterTool,
        UnitConverterTool,
        ImageBase64Tool,
        QrCodeGeneratorTool,
        IpSubnetCalculatorTool,
        HtmlEntitiesTool,
        LoremIpsumGeneratorTool,
        UserAgentParserTool,
        SqlFormatterTool,
        CertificateDecoderTool,
        JwtEncoderTool,
        TimezoneConverterTool,
        EnvParserTool,
        CookieParserTool,
    ):
        context.tool_registry.register(tool_cls)

    logger = get_logger("startup")
    logger.info("Registered %d tools", len(context.tool_registry.get_all()))


if __name__ == "__main__":
    sys.exit(main())
