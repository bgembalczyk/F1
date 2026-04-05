import json
from typing import Any

from scrapers.base.export.metadata import ExportMetadata
from scrapers.base.format.formatter_helpers import extract_data
from scrapers.base.results import ScrapeResult


class JsonFormatter:
    _PINNED_FRONT_KEYS: tuple[str, ...] = ("constructor", "engine", "manufacturer")

    def format(
        self,
        result: ScrapeResult,
        *,
        indent: int = 2,
        include_metadata: bool = False,
    ) -> str:
        payload = self._json_payload(result, include_metadata=include_metadata)
        return json.dumps(
            self._sort_nested_dict_keys(payload),
            ensure_ascii=False,
            indent=indent,
        )

    @classmethod
    def _sort_nested_dict_keys(cls, value: Any) -> Any:
        if isinstance(value, dict):
            return {
                key: cls._sort_nested_dict_keys(value[key])
                for key in sorted(value, key=cls._dict_key_sort_key)
            }
        if isinstance(value, list):
            return [cls._sort_nested_dict_keys(item) for item in value]
        return value

    @classmethod
    def _dict_key_sort_key(cls, key: Any) -> tuple[int, str]:
        if isinstance(key, str) and key in cls._PINNED_FRONT_KEYS:
            return (cls._PINNED_FRONT_KEYS.index(key), key)
        return (len(cls._PINNED_FRONT_KEYS), str(key))

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
