import json
from typing import Any

from scrapers.base.errors import SourceParseError


class GeminiResponseParser:
    """Mapuje surową odpowiedź Gemini API na wynik biznesowy."""

    def parse(self, api_response: dict[str, Any]) -> dict[str, Any]:
        candidates = api_response.get("candidates") or [{}]
        parts = candidates[0].get("content", {}).get("parts") or [{}]
        text = parts[0].get("text")

        if text is None:
            raise SourceParseError(
                message="Gemini API response does not contain text payload.",
                source_name="gemini",
            )

        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise SourceParseError(
                message="Gemini text payload is not valid JSON.",
                source_name="gemini",
                cause=exc,
            ) from exc
