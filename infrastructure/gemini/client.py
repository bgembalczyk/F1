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

import ssl
from pathlib import Path
from typing import Any

import certifi

from infrastructure.gemini.cache import GeminiCache
from infrastructure.gemini.cache_service import GeminiCacheService
from infrastructure.gemini.constants import DEFAULT_KEY_FILE
from infrastructure.gemini.constants import DEFAULT_MODELS
from infrastructure.gemini.constants import DEFAULT_TIMEOUT
from infrastructure.gemini.model_config import ModelConfig
from infrastructure.gemini.model_selector import ModelSelector
from infrastructure.gemini.model_state import ModelState
from infrastructure.gemini.orchestration import GeminiOrchestrationService
from infrastructure.gemini.response_parser import GeminiResponseParser
from infrastructure.gemini.transport import GeminiTransport


class GeminiClient:
    """Cienki klient-orchestrator dla modułów Gemini."""

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

        self._ssl_context = self._build_ssl_context()
        self._model_selector = ModelSelector(models)
        self._cache_service = GeminiCacheService(cache)
        self._transport = GeminiTransport(
            api_key=api_key,
            timeout=timeout,
            ssl_context=self._ssl_context,
        )
        self._response_parser = GeminiResponseParser()
        self._orchestration = GeminiOrchestrationService(
            model_selector=self._model_selector,
            cache_service=self._cache_service,
        )

        # Backward-compatible reference used by existing tests.
        self._model_states = self._model_selector.model_states

    @classmethod
    def from_key_file(
        cls,
        key_file: Path | str | None = None,
        *,
        models: list[ModelConfig] | None = None,
        cache: GeminiCache | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> "GeminiClient":
        """Tworzy klienta wczytując klucz API z pliku."""
        path = Path(key_file) if key_file else DEFAULT_KEY_FILE
        if not path.exists():
            msg = (
                f"Plik z kluczem Gemini API nie istnieje: {path}\n"
                "Utwórz plik i wpisz do niego swój klucz API (tylko klucz, bez spacji)."
            )
            raise FileNotFoundError(msg)

        api_key = path.read_text(encoding="utf-8").strip()
        return cls(
            api_key,
            models=models if models is not None else list(DEFAULT_MODELS),
            cache=cache,
            timeout=timeout,
        )

    def query(
        self,
        prompt: str,
        *,
        response_mime_type: str = "application/json",
    ) -> dict[str, Any]:
        return self._orchestration.run(
            prompt,
            response_mime_type=response_mime_type,
            call_api=lambda model: self._call_api(
                prompt,
                model=model,
                response_mime_type=response_mime_type,
            ),
        )

    def _call_api(
        self,
        prompt: str,
        *,
        model: str,
        response_mime_type: str,
    ) -> dict[str, Any]:
        api_response = self._transport.generate(
            prompt,
            model=model,
            response_mime_type=response_mime_type,
        )
        return self._response_parser.parse(api_response)

    @staticmethod
    def _build_ssl_context() -> ssl.SSLContext:
        """Buduje kontekst SSL oparty o certyfikaty certifi."""
        return ssl.create_default_context(cafile=certifi.where())
