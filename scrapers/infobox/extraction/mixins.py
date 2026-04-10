from __future__ import annotations

from typing import Any


class ParsedRecordsMixin:
    """Shared coercion helpers for infobox extraction pipelines."""

    @staticmethod
    def coerce_records(raw_result: Any) -> list[dict[str, Any]]:
        if raw_result is None:
            return []
        if isinstance(raw_result, dict):
            return [raw_result]
        if isinstance(raw_result, list):
            return [record for record in raw_result if isinstance(record, dict)]
        msg = f"Unsupported infobox parser result: {type(raw_result)!r}"
        raise TypeError(msg)
