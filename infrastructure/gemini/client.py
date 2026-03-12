"""Klient Gemini API z obsługą cache.

Klucz API powinien znajdować się w pliku ``config/gemini_api_key.txt``
(względem katalogu repo). Plik ten jest wykluczony z repozytorium przez
``.gitignore``.

Przykład użycia::

    from infrastructure.gemini.client import GeminiClient, ModelConfig
    models = [
        ModelConfig("gemini-2.5-flash-lite", requests_per_minute=9, requests_per_day=1500),
    ]
    client = GeminiClient.from_key_file(models=models)
    result = client.query(prompt)
"""

import json
import ssl
import threading
import time
import urllib.error
import urllib.request
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

import certifi

from infrastructure.gemini.cache import GeminiCache


@dataclass
class ModelConfig:
    """Konfiguracja pojedynczego modelu Gemini z limitami zapytań.

    Parameters
    ----------
    model:
        Nazwa modelu, np. ``"gemini-2.5-flash-lite"``.
    requests_per_minute:
        Maksymalna liczba zapytań na minutę (RPM).
    requests_per_day:
        Maksymalna liczba zapytań na dobę (RPD).
    """

    model: str
    requests_per_minute: int
    requests_per_day: int


_API_URL_TEMPLATE = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "{model}:generateContent?key={api_key}"
)
_DEFAULT_KEY_FILE = Path(__file__).resolve().parents[2] / "config" / "gemini_api_key.txt"
_DEFAULT_TIMEOUT = 30

# Domyślna lista modeli używana przez from_key_file() gdy models nie zostanie podane.
_DEFAULT_MODELS: List[ModelConfig] = [
    ModelConfig(
        model="gemini-3.1-flash-lite-preview",
        requests_per_minute=15,
        requests_per_day=500,
    ),
    ModelConfig(
        model="gemini-3-flash-preview",
        requests_per_minute=5,
        requests_per_day=20,
    ),
    ModelConfig(
        model="gemini-2.5-flash",
        requests_per_minute=5,
        requests_per_day=20,
    ),
    ModelConfig(
        model="gemini-2.5-flash-lite",
        requests_per_minute=10,
        requests_per_day=20,
    ),
    ModelConfig(
        model="gemini-2.5-flash-lite-preview-09-2025",
        requests_per_minute=10,
        requests_per_day=20,
    ),
    ModelConfig(
        model="gemma-3-27b-it",
        requests_per_minute=30,
        requests_per_day=14400,
    ),
    ModelConfig(
        model="gemma-3-12b-it",
        requests_per_minute=30,
        requests_per_day=14400,
    ),
    ModelConfig(
        model="gemma-3-4b-it",
        requests_per_minute=30,
        requests_per_day=14400,
    ),
    ModelConfig(
        model="gemma-3-2b-it",
        requests_per_minute=30,
        requests_per_day=14400,
    ),
    ModelConfig(
        model="gemma-3-1b-it",
        requests_per_minute=30,
        requests_per_day=14400,
    ),
]


class _ModelState:
    """Wewnętrzny stan rate-limitera dla jednego modelu (sliding window)."""

    _RPM_WINDOW = 60.0      # okno dla RPM w sekundach
    _RPD_WINDOW = 86400.0   # okno dla RPD w sekundach (24 h)

    def __init__(self, config: ModelConfig) -> None:
        self.config = config
        self._rpm_timestamps: deque[float] = deque()
        self._rpd_timestamps: deque[float] = deque()

    @property
    def model(self) -> str:
        return self.config.model

    def is_available(self, now: float) -> bool:
        """Sprawdza, czy model nie przekroczył żadnego z limitów."""
        self._purge_rpm(now)
        self._purge_rpd(now)
        return (
            len(self._rpm_timestamps) < self.config.requests_per_minute
            and len(self._rpd_timestamps) < self.config.requests_per_day
        )

    def record_request(self, now: float) -> None:
        """Rejestruje znacznik czasu nowego zapytania."""
        self._rpm_timestamps.append(now)
        self._rpd_timestamps.append(now)

    def _purge_rpm(self, now: float) -> None:
        while self._rpm_timestamps and now - self._rpm_timestamps[0] >= self._RPM_WINDOW:
            self._rpm_timestamps.popleft()

    def _purge_rpd(self, now: float) -> None:
        while self._rpd_timestamps and now - self._rpd_timestamps[0] >= self._RPD_WINDOW:
            self._rpd_timestamps.popleft()


class GeminiClient:
    """Klient REST API Gemini z obsługą cache i fallbackiem na wiele modeli.

    Modele są wypróbowywane zgodnie z podaną hierarchią:

    * Jeśli bieżący model osiągnął limit RPM lub RPD, przechodzi się do
      następnego modelu na liście.
    * Jeśli zapytanie zwróci błąd odpowiedzi, jest powtarzane dla
      następnego modelu.
    * Gdy lista modeli się wyczerpie, rzucany jest wyjątek.
    """

    def __init__(
        self,
        api_key: str,
        *,
        models: List[ModelConfig],
        cache: Optional[GeminiCache] = None,
        timeout: int = _DEFAULT_TIMEOUT,
    ) -> None:
        if not api_key:
            raise ValueError("Gemini API key nie może być pusty.")
        if not models:
            raise ValueError("Lista modeli nie może być pusta.")
        self._api_key = api_key
        self._model_states = [_ModelState(m) for m in models]
        self._cache = cache if cache is not None else GeminiCache()
        self._timeout = timeout
        self._ssl_context = self._build_ssl_context()
        self._rate_lock = threading.Lock()

    # ------------------------------------------------------------------
    # factory
    # ------------------------------------------------------------------

    @classmethod
    def from_key_file(
        cls,
        key_file: Path | str | None = None,
        *,
        models: Optional[List[ModelConfig]] = None,
        cache: Optional[GeminiCache] = None,
        timeout: int = _DEFAULT_TIMEOUT,
    ) -> "GeminiClient":
        """Tworzy klienta wczytując klucz API z pliku.

        Domyślna ścieżka pliku z kluczem: ``config/gemini_api_key.txt``
        (w katalogu głównym repozytorium).

        Jeśli *models* nie zostanie podane, używana jest domyślna lista
        :data:`_DEFAULT_MODELS`.
        """
        path = Path(key_file) if key_file else _DEFAULT_KEY_FILE
        if not path.exists():
            raise FileNotFoundError(
                f"Plik z kluczem Gemini API nie istnieje: {path}\n"
                "Utwórz plik i wpisz do niego swój klucz API (tylko klucz, bez spacji)."
            )
        api_key = path.read_text(encoding="utf-8").strip()
        return cls(
            api_key,
            models=models if models is not None else list(_DEFAULT_MODELS),
            cache=cache,
            timeout=timeout,
        )

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

        Korzysta z hierarchii modeli:
        – jeśli model osiągnął limit RPM lub RPD, przełącza na następny,
        – jeśli model zwróci błąd, ponawia zapytanie na następnym modelu,
        – jeśli wyczerpią się modele, rzuca wyjątkiem.

        Wynik z cache jest zwracany tylko jeśli pasuje zarówno *prompt*,
        jak i aktualnie wybrany model.
        """
        error_models: Set[str] = set()

        while True:
            model = self._pick_model(exclude=error_models)
            if model is None:
                raise RuntimeError(
                    "Wszystkie dostępne modele Gemini są wyczerpane lub osiągnęły limit.\n"
                    f"Modele z błędem API: {error_models or '(brak)'}\n"
                    f"Dostępne modele: {[s.model for s in self._model_states]}"
                )

            cached = self._cache.get(prompt, model)
            if cached is not None:
                print(f"[GeminiClient] Cache hit (model={model}), pomijam wywołanie API.")
                return cached

            try:
                result = self._call_api(prompt, model=model, response_mime_type=response_mime_type)
            except RuntimeError:
                error_models.add(model)
                continue

            self._cache.set(prompt, model, result)
            return result

    # ------------------------------------------------------------------
    # internal
    # ------------------------------------------------------------------

    def _pick_model(self, exclude: Set[str]) -> Optional[str]:
        """Zwraca nazwę pierwszego dostępnego modelu (nie przekroczył RPM/RPD
        i nie jest w *exclude*), lub ``None`` gdy żaden model nie jest
        dostępny.

        Operacja jest atomowa (trzyma blokadę), aby uniknąć wyścigów wątków.
        """
        with self._rate_lock:
            now = time.monotonic()
            for state in self._model_states:
                if state.model in exclude:
                    continue
                if state.is_available(now):
                    state.record_request(now)
                    return state.model
        return None

    def _call_api(self, prompt: str, *, model: str, response_mime_type: str) -> Dict[str, Any]:
        url = _API_URL_TEMPLATE.format(model=model, api_key=self._api_key)
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

        print(f"[GeminiClient] >>> Zapytanie do API (model={model}):")
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

    @staticmethod
    def _build_ssl_context() -> ssl.SSLContext:
        """Buduje kontekst SSL oparty o certyfikaty certifi."""
        return ssl.create_default_context(cafile=certifi.where())
