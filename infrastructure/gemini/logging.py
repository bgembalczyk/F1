"""Logging helpers for Gemini integration with sensitive-data redaction."""

from __future__ import annotations

import logging
from typing import Any, Protocol

SENSITIVE_FIELDS = frozenset(
    {
        "prompt",
        "raw_response",
        "api_response",
        "response_text",
        "payload",
        "request_body",
    },
)


class ProgressReporter(Protocol):
    """Simple progress reporting protocol used across app components."""

    def debug(self, event: str, **fields: Any) -> None:
        ...

    def info(self, event: str, **fields: Any) -> None:
        ...

    def warn(self, event: str, **fields: Any) -> None:
        ...

    def error(self, event: str, **fields: Any) -> None:
        ...


class RedactingLogger:
    """Adapter over ``logging.Logger`` that redacts sensitive fields."""

    def __init__(
        self,
        logger: logging.Logger | None = None,
        *,
        sensitive_fields: set[str] | frozenset[str] = SENSITIVE_FIELDS,
    ) -> None:
        self._logger = logger if logger is not None else logging.getLogger(__name__)
        self._sensitive_fields = {field.lower() for field in sensitive_fields}

    def debug(self, event: str, **fields: Any) -> None:
        self._emit(logging.DEBUG, event, fields)

    def info(self, event: str, **fields: Any) -> None:
        self._emit(logging.INFO, event, fields)

    def warn(self, event: str, **fields: Any) -> None:
        self._emit(logging.WARNING, event, fields)

    def error(self, event: str, **fields: Any) -> None:
        self._emit(logging.ERROR, event, fields)

    def _emit(self, level: int, event: str, fields: dict[str, Any]) -> None:
        sanitized = {key: self._sanitize(key, value) for key, value in fields.items()}
        if sanitized:
            context = ", ".join(f"{key}={value!r}" for key, value in sorted(sanitized.items()))
            self._logger.log(level, "%s | %s", event, context)
            return
        self._logger.log(level, "%s", event)

    def _sanitize(self, key: str, value: Any) -> Any:
        if key.lower() in self._sensitive_fields:
            return "[REDACTED]"
        return value


__all__ = ["ProgressReporter", "RedactingLogger", "SENSITIVE_FIELDS"]
