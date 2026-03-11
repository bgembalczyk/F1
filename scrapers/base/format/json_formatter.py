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
            include_metadata: bool = False,
    ) -> str:
        payload = self._json_payload(result, include_metadata=include_metadata)
        return json.dumps(payload, ensure_ascii=False, indent=indent)

    @staticmethod
    def _json_payload(
            result: ScrapeResult,
            *,
            include_metadata: bool = False,
    ) -> Any:
        data = extract_data(result)
        if include_metadata:
            metadata = ExportMetadata.from_result(result)
            return {
                "meta": metadata.to_dict(),
                "data": data,
            }
        return data
