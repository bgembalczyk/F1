import json
from typing import Any


class GeminiResponseParser:
    """Mapuje surową odpowiedź Gemini API na wynik biznesowy."""

    def parse(self, api_response: dict[str, Any]) -> dict[str, Any]:
        candidates = api_response.get("candidates") or [{}]
        parts = candidates[0].get("content", {}).get("parts") or [{}]
        text = parts[0].get("text")

        if text is None:
            msg = (
                "Gemini API nie zwróciło pola candidates[0].content.parts[0].text.\n"
                "Pełna odpowiedź:\n"
                f"{json.dumps(api_response, ensure_ascii=False, indent=2)}"
            )
            raise RuntimeError(msg)

        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            msg = (
                "Gemini zwróciło tekst, który nie jest poprawnym JSON-em.\n"
                f"Text:\n{text}\n\n"
                "Pełna odpowiedź API:\n"
                f"{json.dumps(api_response, ensure_ascii=False, indent=2)}"
            )
            raise RuntimeError(msg) from exc
