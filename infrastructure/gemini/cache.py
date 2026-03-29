from pathlib import Path
from typing import Any

from infrastructure.cache.file_ttl_cache import FileTtlCache
from infrastructure.cache.file_ttl_cache import GeminiJsonFileCacheAdapter
from infrastructure.gemini.constants import ONE_YEAR_SECONDS


class GeminiCache:
    """Cache JSON odpowiedzi Gemini oparty o pliki z TTL.

    Klucz cache to para (model, pytanie) — hash SHA-256 z ciągu
    ``"{model}:{question}"``.  Wynik jest zwracany z cache tylko wtedy,
    gdy zgadzają się oba składniki klucza.
    Domyślnie odpowiedzi są ważne przez rok.

    Lokalizacja domyślna (poza repo): ``data/gemini_cache``
    - katalog ten jest dodany do ``.gitignore``.
    """

    def __init__(
        self,
        *,
        cache_dir: Path | str | None = None,
        ttl_seconds: int = ONE_YEAR_SECONDS,
    ) -> None:
        if cache_dir is None:
            # Domyślna ścieżka: <repo_root>/data/gemini_cache
            cache_dir = Path(__file__).resolve().parents[2] / "data" / "gemini_cache"

        self._cache = FileTtlCache[dict[str, Any]](
            cache_dir=cache_dir,
            ttl_seconds=ttl_seconds,
            adapter=GeminiJsonFileCacheAdapter(),
        )

    def get(self, question: str, model: str) -> dict[str, Any] | None:
        """Zwraca zbuforowaną odpowiedź lub ``None`` gdy brak/przestarzała.

        Wynik z cache jest zwracany tylko jeśli zgadza się zarówno *question*
        jak i *model*.
        """
        return self._cache.get(self._cache_key(question, model))

    def set(self, question: str, model: str, response: dict[str, Any]) -> None:
        """Zapisuje odpowiedź do cache."""
        self._cache.set(self._cache_key(question, model), response)

    def _cache_key(self, question: str, model: str) -> str:
        return f"{model}:{question}"
