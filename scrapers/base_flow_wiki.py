from __future__ import annotations

from typing import Any


class BaseOrchestrationFlow:
    @staticmethod
    def _deduplicate_by_url(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen: set[str] = set()
        normalized: list[dict[str, Any]] = []
        for record in records:
            url = str(record.get("url", "")).strip()
            if not url or url in seen:
                continue
            seen.add(url)
            normalized.append({"name": str(record.get("name", "")), "url": url})
        return normalized
