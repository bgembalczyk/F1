import json
from typing import Any

from scrapers.base.export.metadata import ExportMetadata
from scrapers.base.format.formatter_helpers import extract_data
from scrapers.base.results import ScrapeResult


class JsonFormatter:
    def format(
        self,
        result: ScrapeResult,
        *,
        indent: int = 2,
    ) -> str:
        payload = self._json_payload(result)
        return json.dumps(payload, ensure_ascii=False, indent=indent)

    @staticmethod
    def _json_payload(
        result: ScrapeResult,
    ) -> Any:
        metadata = ExportMetadata.from_result(result)
        return {
            "meta": metadata.to_dict(),
            "data": extract_data(result),
        }
