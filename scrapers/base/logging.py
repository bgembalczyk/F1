from __future__ import annotations

import json
import logging
from collections.abc import Callable
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any

from scrapers.base.constants.runtime import LOGGER_NAME

_DEFAULT_EXECUTION_CONTEXT: dict[str, str | None] = {
    "run_id": None,
    "seed": None,
    "domain": None,
    "source": None,
    "step": None,
    "status": None,
}


class JsonLinesFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "level": record.levelname.lower(),
            "logger": record.name,
            "message": record.getMessage(),
            "run_id": getattr(record, "run_id", None),
            "domain": getattr(record, "domain", None),
            "seed": getattr(record, "seed", None),
            "source": getattr(record, "source", None),
            "step": getattr(record, "step", None),
            "status": getattr(record, "status", None),
        }
        return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def configure_logging(*, verbose: bool = False, trace: bool = False) -> None:
    level = logging.DEBUG if trace else logging.INFO if verbose else logging.WARNING
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
    step: str | None = None,
    status: str | None = None,
) -> dict[str, str | None]:
    return {
        "run_id": run_id,
        "seed": seed_name,
        "domain": domain,
        "source": source_name,
        "step": step,
        "status": status,
    }


def get_logger(
    scraper_name: str,
    *,
    execution_context: dict[str, str | None] | None = None,
) -> logging.LoggerAdapter:
    base_logger = logging.getLogger(f"{LOGGER_NAME}.{scraper_name}")
    context = _DEFAULT_EXECUTION_CONTEXT | (execution_context or {})
    return logging.LoggerAdapter(base_logger, {"scraper": scraper_name, **context})


class RunTraceWriter:
    def __init__(
        self,
        trace_path: Path,
        *,
        timestamp_provider: Callable[[], str] | None = None,
    ) -> None:
        self._trace_path = trace_path
        self._trace_path.parent.mkdir(parents=True, exist_ok=True)
        self._timestamp_provider = timestamp_provider or (
            lambda: datetime.now(tz=timezone.utc).isoformat()
        )

    @property
    def trace_path(self) -> Path:
        return self._trace_path

    def write(self, *, event: dict[str, Any]) -> None:
        payload = {
            "timestamp": self._timestamp_provider(),
            **event,
        }
        with self._trace_path.open("a", encoding="utf-8") as trace_file:
            trace_file.write(
                f"{json.dumps(payload, ensure_ascii=False, sort_keys=True)}\n",
            )
