"""Klient Gemini API z obsługą cache.

Klucz API powinien znajdować się w pliku ``config/gemini_api_key.txt``
(względem katalogu repo).  Plik ten jest wykluczony z repozytorium przez
``.gitignore``.

Przykład użycia::

    from infrastructure.gemini.client import GeminiClient
    client = GeminiClient.from_key_file()
    result = client.query(prompt)
"""

import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Optional

from infrastructure.gemini.cache import GeminiCache


_DEFAULT_MODEL = "gemini-2.0-flash"
_API_URL_TEMPLATE = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "{model}:generateContent?key={api_key}"
)
_DEFAULT_KEY_FILE = Path(__file__).resolve().parents[3] / "config" / "gemini_api_key.txt"


class GeminiClient:
    """Prosty klient REST API Gemini z opcjonalnym cache."""

    def __init__(
            self,
            api_key: str,
            *,
            model: str = _DEFAULT_MODEL,
            cache: Optional[GeminiCache] = None,
    ) -> None:
        if not api_key:
            raise ValueError("Gemini API key nie może być pusty.")
        self._api_key = api_key
        self._model = model
        self._cache = cache if cache is not None else GeminiCache()

    # ------------------------------------------------------------------
    # factory
    # ------------------------------------------------------------------

    @classmethod
    def from_key_file(
            cls,
            key_file: Path | str | None = None,
            *,
            model: str = _DEFAULT_MODEL,
            cache: Optional[GeminiCache] = None,
    ) -> "GeminiClient":
        """Tworzy klienta wczytując klucz API z pliku.

        Domyślna ścieżka pliku z kluczem: ``config/gemini_api_key.txt``
        (w katalogu głównym repozytorium).
        """
        path = Path(key_file) if key_file else _DEFAULT_KEY_FILE
        if not path.exists():
            raise FileNotFoundError(
                f"Plik z kluczem Gemini API nie istnieje: {path}\n"
                "Utwórz plik i wpisz do niego swój klucz API (tylko klucz, bez spacji)."
            )
        api_key = path.read_text(encoding="utf-8").strip()
        return cls(api_key, model=model, cache=cache)

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def query(self, prompt: str, *, response_mime_type: str = "application/json") -> Dict[str, Any]:
        """Wysyła zapytanie do Gemini i zwraca odpowiedź jako słownik.

        Jeśli dokładnie to samo pytanie było już zadane i odpowiedź
        jest młodsza niż TTL cache, zwraca wynik z cache.
        """
        cached = self._cache.get(prompt)
        if cached is not None:
            return cached

        result = self._call_api(prompt, response_mime_type=response_mime_type)
        self._cache.set(prompt, result)
        return result

    # ------------------------------------------------------------------
    # internal
    # ------------------------------------------------------------------

    def _call_api(self, prompt: str, *, response_mime_type: str) -> Dict[str, Any]:
        url = _API_URL_TEMPLATE.format(model=self._model, api_key=self._api_key)
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": response_mime_type},
        }
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        print(f"[GeminiClient] >>> Zapytanie do API (model={self._model}):")
        print(prompt)

        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
            raw = resp.read().decode("utf-8")

        print("[GeminiClient] <<< Odpowiedź surowa od API:")
        print(raw)

        api_response = json.loads(raw)
        text = (
            api_response
            .get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "{}")
        )
        return json.loads(text)
