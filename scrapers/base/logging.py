from __future__ import annotations

import json
import logging
from datetime import datetime
from datetime import timezone
from typing import Any

from scrapers.base.constants.runtime import LOGGER_NAME
from scrapers.base.debug_contract import DebugMode
from scrapers.base.debug_contract import resolve_debug_contract


_DEFAULT_EXECUTION_CONTEXT: dict[str, str | None] = {
    "run_id": None,
    "seed_name": None,
    "domain": None,
    "source_name": None,
}


class JsonLinesFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "level": record.levelname.lower(),
            "logger": record.name,
            "message": record.getMessage(),
            "run_id": getattr(record, "run_id", None),
            "seed_name": getattr(record, "seed_name", None),
            "domain": getattr(record, "domain", None),
            "source_name": getattr(record, "source_name", None),
        }
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(*, debug_mode: DebugMode = DebugMode.OFF) -> None:
    level = resolve_debug_contract(debug_mode).log_level
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    if root_logger.handlers:
        for handler in root_logger.handlers:
            handler.setLevel(level)
            handler.setFormatter(JsonLinesFormatter())
        return

    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(JsonLinesFormatter())
    root_logger.addHandler(handler)


def build_execution_context(
    *,
    run_id: str | None = None,
    seed_name: str | None = None,
    domain: str | None = None,
    source_name: str | None = None,
) -> dict[str, str | None]:
    return {
        "run_id": run_id,
        "seed_name": seed_name,
        "domain": domain,
        "source_name": source_name,
    }


def get_logger(
    scraper_name: str,
    *,
    execution_context: dict[str, str | None] | None = None,
) -> logging.LoggerAdapter:
    base_logger = logging.getLogger(f"{LOGGER_NAME}.{scraper_name}")
    context = _DEFAULT_EXECUTION_CONTEXT | (execution_context or {})
    return logging.LoggerAdapter(base_logger, {"scraper": scraper_name, **context})
