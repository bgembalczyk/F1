from __future__ import annotations

import json
from typing import Any

from scrapers.base.format.formatter_helpers import _extract_data
from scrapers.base.results import ScrapeResult


class JsonFormatter:
    def format(
        self,
        result: ScrapeResult,
        *,
        indent: int = 2,
        include_metadata: bool = False,
    ) -> str:
        payload = self._json_payload(result, include_metadata=include_metadata)
        return json.dumps(payload, ensure_ascii=False, indent=indent)

    def _json_payload(
        self,
        result: ScrapeResult,
        *,
        include_metadata: bool,
    ) -> Any:
        if not include_metadata:
            return _extract_data(result)

        return {
            "meta": {
                "source_url": result.source_url,
                "timestamp": result.timestamp.isoformat(),
            },
            "data": _extract_data(result),
        }
