"""Klient Gemini API z obsługą cache.

Klucz API powinien znajdować się w pliku ``config/gemini_api_key.txt``
(względem katalogu repo). Plik ten jest wykluczony z repozytorium przez
``.gitignore``.

Przykład użycia::

    from infrastructure.gemini.client import GeminiClient, ModelConfig
    models = [
        ModelConfig(
            "gemini-2.5-flash-lite",
            requests_per_minute=9,
            requests_per_day=1500,
        ),
    ]
    client = GeminiClient.from_key_file(models=models)
    result = client.query(prompt)
"""

import json
import ssl
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import certifi

from infrastructure.gemini.cache import GeminiCache
from infrastructure.gemini.constants import API_URL_TEMPLATE
from infrastructure.gemini.constants import DEFAULT_KEY_FILE
from infrastructure.gemini.constants import DEFAULT_MODELS
from infrastructure.gemini.constants import DEFAULT_TIMEOUT
from infrastructure.gemini.errors import GeminiHttpError
from infrastructure.gemini.errors import GeminiRateLimitExhaustedError
from infrastructure.gemini.errors import GeminiResponseParseError
from infrastructure.gemini.errors import GeminiTransportError
from infrastructure.gemini.model_config import ModelConfig
from infrastructure.gemini.model_state import ModelState


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
        models: list[ModelConfig],
        cache: GeminiCache | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        if not api_key:
            msg = "Gemini API key nie może być pusty."
            raise ValueError(msg)
        if not models:
            msg = "Lista modeli nie może być pusta."
            raise ValueError(msg)
        self._api_key = api_key
        self._model_states = [ModelState(m) for m in models]
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
        models: list[ModelConfig] | None = None,
        cache: GeminiCache | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> "GeminiClient":
        """Tworzy klienta wczytując klucz API z pliku.

        Domyślna ścieżka pliku z kluczem: ``config/gemini_api_key.txt``
        (w katalogu głównym repozytorium).

        Jeśli *models* nie zostanie podane, używana jest domyślna lista
        :data:`_DEFAULT_MODELS`.
        """
        path = Path(key_file) if key_file else DEFAULT_KEY_FILE
        if not path.exists():
            msg = (
                f"Plik z kluczem Gemini API nie istnieje: {path}\n"
                "Utwórz plik i wpisz do niego swój klucz API (tylko klucz, bez spacji)."
            )
            raise FileNotFoundError(
                msg,
            )
        api_key = path.read_text(encoding="utf-8").strip()
        return cls(
            api_key,
            models=models if models is not None else list(DEFAULT_MODELS),
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
    ) -> dict[str, Any]:
        """Wysyła zapytanie do Gemini i zwraca odpowiedź jako słownik.

        Korzysta z hierarchii modeli:
        - jeśli model osiągnął limit RPM lub RPD, przełącza na następny,
        - jeśli model zwróci błąd, ponawia zapytanie na następnym modelu,
        - jeśli wyczerpią się modele, rzuca wyjątkiem.

        Wynik z cache jest zwracany tylko jeśli pasuje zarówno *prompt*,
        jak i aktualnie wybrany model.
        """
        error_models: set[str] = set()

        while True:
            model = self._pick_model(exclude=error_models)
            if model is None:
                msg = (
                    "Wszystkie dostępne modele Gemini są wyczerpane "
                    "lub osiągnęły limit.\n"
                    f"Modele z błędem API: {error_models or '(brak)'}\n"
                    f"Dostępne modele: {[s.model for s in self._model_states]}"
                )
                raise GeminiRateLimitExhaustedError(
                    msg,
                )

            cached = self._cache.get(prompt, model)
            if cached is not None:
                print(
                    f"[GeminiClient] Cache hit (model={model}), pomijam wywołanie API.",
                )
                return cached

            try:
                result = self._call_api(
                    prompt,
                    model=model,
                    response_mime_type=response_mime_type,
                )
            except GeminiTransportError:
                error_models.add(model)
                continue
            except GeminiHttpError:
                error_models.add(model)
                continue
            except GeminiResponseParseError:
                error_models.add(model)
                continue

            self._cache.set(prompt, model, result)
            return result

    # ------------------------------------------------------------------
    # internal
    # ------------------------------------------------------------------

    def _pick_model(self, exclude: set[str]) -> str | None:
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

    def _call_api(
        self,
        prompt: str,
        *,
        model: str,
        response_mime_type: str,
    ) -> dict[str, Any]:
        url = API_URL_TEMPLATE.format(model=model, api_key=self._api_key)
        parsed_url = urllib.parse.urlparse(url)
        if parsed_url.scheme != "https":
            msg = "Gemini API endpoint musi używać schematu https."
            raise GeminiTransportError(msg)
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": response_mime_type},
        }
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(  # noqa: S310
            parsed_url.geturl(),
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        print(f"[GeminiClient] >>> Zapytanie do API (model={model}):")
        print(prompt)

        try:
            req_url = req.full_url
            parsed_req_url = urllib.parse.urlparse(req_url)
            if parsed_req_url.scheme != "https":
                msg = "Żądanie Gemini API musi używać schematu https."
                raise GeminiTransportError(msg)

            with urllib.request.urlopen(  # noqa: S310
                req,
                timeout=self._timeout,
                context=self._ssl_context,
            ) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            msg = (
                f"Gemini API zwróciło HTTP {exc.code}: {exc.reason}\n"
                f"Response body:\n{error_body}"
            )
            raise GeminiHttpError(
                msg,
            ) from exc
        except urllib.error.URLError as exc:
            msg = (
                "Nie udało się połączyć z Gemini API. "
                "Sprawdź połączenie sieciowe, SSL/certyfikaty oraz\n"
                "poprawność endpointu.\n"
                f"Szczegóły: {exc}"
            )
            raise GeminiTransportError(
                msg,
            ) from exc

        print("[GeminiClient] <<< Odpowiedź surowa od API:")
        print(raw)

        try:
            api_response = json.loads(raw)
        except json.JSONDecodeError as exc:
            msg = f"Gemini API zwróciło niepoprawny JSON:\n{raw}"
            raise GeminiResponseParseError(
                msg,
            ) from exc

        text = (
            api_response.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text")
        )

        if text is None:
            msg = (
                "Gemini API nie zwróciło pola candidates[0].content.parts[0].text.\n"
                "Pełna odpowiedź:\n"
                f"{json.dumps(api_response, ensure_ascii=False, indent=2)}"
            )
            raise GeminiResponseParseError(
                msg,
            )

        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            msg = (
                "Gemini zwróciło tekst, który nie jest poprawnym JSON-em.\n"
                f"Text:\n{text}\n\n"
                "Pełna odpowiedź API:\n"
                f"{json.dumps(api_response, ensure_ascii=False, indent=2)}"
            )
            raise GeminiResponseParseError(
                msg,
            ) from exc

    @staticmethod
    def _build_ssl_context() -> ssl.SSLContext:
        """Buduje kontekst SSL oparty o certyfikaty certifi."""
        return ssl.create_default_context(cafile=certifi.where())
