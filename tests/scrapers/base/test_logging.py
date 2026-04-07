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


def test_configure_logging_verbose_sets_info_level() -> None:
    # Lines 44-57
    root = logging.getLogger()
    original_handlers = list(root.handlers)
    original_level = root.level

    try:
        # Remove existing handlers to test fresh setup
        root.handlers.clear()
        configure_logging(verbose=True)
        assert root.level == logging.INFO
    finally:
        root.handlers.clear()
        root.handlers.extend(original_handlers)
        root.setLevel(original_level)


def test_configure_logging_trace_sets_debug_level() -> None:
    root = logging.getLogger()
    original_handlers = list(root.handlers)
    original_level = root.level

    try:
        root.handlers.clear()
        configure_logging(trace=True)
        assert root.level == logging.DEBUG
    finally:
        root.handlers.clear()
        root.handlers.extend(original_handlers)
        root.setLevel(original_level)


def test_configure_logging_with_existing_handlers_updates_them() -> None:
    root = logging.getLogger()
    original_handlers = list(root.handlers)
    original_level = root.level

    try:
        # Add a handler first
        handler = logging.StreamHandler()
        root.addHandler(handler)
        configure_logging(verbose=True)
        assert root.level == logging.INFO
        # Handler should be updated
        assert isinstance(root.handlers[-1].formatter, JsonLinesFormatter)
    finally:
        root.handlers.clear()
        root.handlers.extend(original_handlers)
        root.setLevel(original_level)


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
