"""Klient Gemini API z obsługą cache.

Klucz API powinien znajdować się w pliku ``config/gemini_api_key.txt``
(względem katalogu repo). Plik ten jest wykluczony z repozytorium przez
``.gitignore``.

Przykład użycia::

    from infrastructure.gemini.client import GeminiClient
    client = GeminiClient.from_key_file()
    result = client.query(prompt)
"""

import json
import ssl
import threading
import time
import urllib.error
import urllib.request
from collections import deque
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Optional

import certifi

from infrastructure.gemini.cache import GeminiCache


_DEFAULT_MODEL = "gemini-2.5-flash-lite"

# Limity RPM (requests per minute) per model zgodnie z bezpłatnym tierem Gemini.
_DEFAULT_RPM_LIMITS: Dict[str, int] = {
    "gemini-2.5-flash-lite": 9,
}
_API_URL_TEMPLATE = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "{model}:generateContent?key={api_key}"
)
_DEFAULT_KEY_FILE = Path(__file__).resolve().parents[2] / "config" / "gemini_api_key.txt"
_DEFAULT_TIMEOUT = 30


class GeminiClient:
    """Prosty klient REST API Gemini z opcjonalnym cache."""

    def __init__(
        self,
        api_key: str,
        *,
        model: str = _DEFAULT_MODEL,
        cache: Optional[GeminiCache] = None,
        timeout: int = _DEFAULT_TIMEOUT,
        requests_per_minute: Optional[int] = None,
    ) -> None:
        if not api_key:
            raise ValueError("Gemini API key nie może być pusty.")
        self._api_key = api_key
        self._model = model
        self._cache = cache if cache is not None else GeminiCache()
        self._timeout = timeout
        self._ssl_context = self._build_ssl_context()

        # Rate limiter — sliding window (okno 60 s).
        # Jeśli requests_per_minute nie podano, szukamy domyślnego limitu dla modelu,
        # a jeśli model nie jest znany — wyłączamy limit (None).
        if requests_per_minute is not None:
            self._rpm_limit: Optional[int] = requests_per_minute
        else:
            self._rpm_limit = _DEFAULT_RPM_LIMITS.get(model)
        self._request_timestamps: deque[float] = deque()
        self._rate_lock = threading.Lock()

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
        timeout: int = _DEFAULT_TIMEOUT,
        requests_per_minute: Optional[int] = None,
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
        return cls(api_key, model=model, cache=cache, timeout=timeout, requests_per_minute=requests_per_minute)

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def query(
        self,
        prompt: str,
        *,
        response_mime_type: str = "application/json",
    ) -> Dict[str, Any]:
        """Wysyła zapytanie do Gemini i zwraca odpowiedź jako słownik.

        Jeśli dokładnie to samo pytanie było już zadane i odpowiedź
        jest młodsza niż TTL cache, zwraca wynik z cache.
        """
        cached = self._cache.get(prompt)
        if cached is not None:
            print(f"[GeminiClient] Cache hit (model={self._model}), pomijam wywołanie API.")
            return cached

        result = self._call_api(prompt, response_mime_type=response_mime_type)
        self._cache.set(prompt, result)
        return result

    # ------------------------------------------------------------------
    # internal
    # ------------------------------------------------------------------

    @staticmethod
    def _build_ssl_context() -> ssl.SSLContext:
        """Buduje kontekst SSL oparty o certyfikaty certifi."""
        return ssl.create_default_context(cafile=certifi.where())

    def _throttle(self) -> None:
        """Blokuje wątek, jeśli przekroczono limit RPM (sliding window 60 s)."""
        if self._rpm_limit is None:
            return
        window = 60.0
        with self._rate_lock:
            while True:
                now = time.monotonic()
                # Usuń znaczniki starsze niż 60 s.
                while self._request_timestamps and now - self._request_timestamps[0] >= window:
                    self._request_timestamps.popleft()
                if len(self._request_timestamps) < self._rpm_limit:
                    self._request_timestamps.append(now)
                    return
                # Czekamy do momentu, gdy najstarszy request „wypadnie" z okna.
                sleep_for = window - (now - self._request_timestamps[0])
                print(
                    f"[GeminiClient] Limit RPM ({self._rpm_limit}/min) osiągnięty — "
                    f"czekam {sleep_for:.1f} s."
                )
                # Zwalniamy blokadę na czas oczekiwania, żeby nie blokować innych wątków.
                self._rate_lock.release()
                time.sleep(sleep_for)
                self._rate_lock.acquire()

    def _call_api(self, prompt: str, *, response_mime_type: str) -> Dict[str, Any]:
        self._throttle()
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

        try:
            with urllib.request.urlopen(  # noqa: S310
                req,
                timeout=self._timeout,
                context=self._ssl_context,
            ) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Gemini API zwróciło HTTP {exc.code}: {exc.reason}\n"
                f"Response body:\n{error_body}"
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(
                "Nie udało się połączyć z Gemini API. "
                "Sprawdź połączenie sieciowe, SSL/certyfikaty oraz poprawność endpointu.\n"
                f"Szczegóły: {exc}"
            ) from exc

        print("[GeminiClient] <<< Odpowiedź surowa od API:")
        print(raw)

        try:
            api_response = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"Gemini API zwróciło niepoprawny JSON:\n{raw}"
            ) from exc

        text = (
            api_response
            .get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text")
        )

        if text is None:
            raise RuntimeError(
                "Gemini API nie zwróciło pola candidates[0].content.parts[0].text.\n"
                f"Pełna odpowiedź:\n{json.dumps(api_response, ensure_ascii=False, indent=2)}"
            )

        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Gemini zwróciło tekst, który nie jest poprawnym JSON-em.\n"
                f"Text:\n{text}\n\n"
                f"Pełna odpowiedź API:\n{json.dumps(api_response, ensure_ascii=False, indent=2)}"
            ) from exc