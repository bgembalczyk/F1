# ruff: noqa: E501, PLR2004
import json
import logging

from scrapers.base.logging import JsonLinesFormatter
from scrapers.base.logging import build_execution_context
from scrapers.base.logging import configure_logging
from scrapers.base.logging import get_logger


def test_json_lines_formatter_produces_valid_json() -> None:
    # Lines 28-40: JsonLinesFormatter.format
    formatter = JsonLinesFormatter()
    record = logging.LogRecord(
        name="test.logger",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="hello world",
        args=(),
        exc_info=None,
    )
    output = formatter.format(record)
    parsed = json.loads(output)
    assert parsed["level"] == "info"
    assert parsed["message"] == "hello world"
    assert parsed["logger"] == "test.logger"
    assert "timestamp" in parsed


def test_json_lines_formatter_includes_extra_fields() -> None:
    formatter = JsonLinesFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.WARNING,
        pathname="",
        lineno=0,
        msg="test msg",
        args=(),
        exc_info=None,
    )
    record.run_id = "run-123"
    record.domain = "races"
    output = formatter.format(record)
    parsed = json.loads(output)
    assert parsed["run_id"] == "run-123"
    assert parsed["domain"] == "races"


class TestConfigureLogging:
    def setup_method(self) -> None:
        self.root = logging.getLogger()
        self.original_handlers = list(self.root.handlers)
        self.original_level = self.root.level
        self.root.handlers.clear()

    def teardown_method(self) -> None:
        self.root.handlers.clear()
        self.root.handlers.extend(self.original_handlers)
        self.root.setLevel(self.original_level)

    def test_configure_logging_verbose_sets_info_level(self) -> None:
        # Lines 44-57
        # Remove existing handlers to test fresh setup
        configure_logging(verbose=True)
        assert self.root.level == logging.INFO

    def test_configure_logging_trace_sets_debug_level(self) -> None:
        configure_logging(trace=True)
        assert self.root.level == logging.DEBUG

    def test_configure_logging_with_existing_handlers_updates_them(self) -> None:
        # Add a handler first
        handler = logging.StreamHandler()
        self.root.addHandler(handler)
        configure_logging(verbose=True)
        assert self.root.level == logging.INFO
        # Handler should be updated
        assert isinstance(self.root.handlers[-1].formatter, JsonLinesFormatter)


def test_build_execution_context_returns_full_dict() -> None:
    ctx = build_execution_context(
        run_id="r1",
        seed_name="seed",
        domain="dom",
        source_name="src",
        step="step1",
        status="ok",
    )
    assert ctx == {
        "run_id": "r1",
        "seed": "seed",
        "domain": "dom",
        "source": "src",
        "step": "step1",
        "status": "ok",
    }


def test_get_logger_returns_logger_adapter() -> None:
    adapter = get_logger("test_scraper")
    assert isinstance(adapter, logging.LoggerAdapter)
