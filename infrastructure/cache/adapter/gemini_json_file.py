import json
from typing import Any

from infrastructure.cache.adapter.file_ttl import FileTtlCacheAdapter


class GeminiJsonFileCacheAdapter(FileTtlCacheAdapter[dict[str, Any]]):
    """Adapter cache dla odpowiedzi Gemini (JSON)."""

    extension = ".json"

    def serialize(self, value: dict[str, Any]) -> str:
        if not isinstance(value, dict):
            msg = "Gemini cache payload must be a dictionary."
            raise TypeError(msg)
        try:
            return json.dumps(value, ensure_ascii=False)
        except (TypeError, ValueError) as exc:
            msg = "Gemini cache payload must be JSON serializable."
            raise TypeError(msg) from exc

    def deserialize(self, raw_text: str) -> dict[str, Any]:
        parsed = json.loads(raw_text)
        if not isinstance(parsed, dict):
            msg = "Gemini cache payload must be a JSON object."
            raise TypeError(msg)
        return parsed
