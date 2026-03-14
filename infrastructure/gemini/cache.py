import json
import time
from hashlib import sha256
from pathlib import Path
from typing import Any

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
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = max(0, int(ttl_seconds))

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def get(self, question: str, model: str) -> dict[str, Any] | None:
        """Zwraca zbuforowaną odpowiedź lub ``None`` gdy brak/przestarzała.

        Wynik z cache jest zwracany tylko jeśli zgadza się zarówno *question*
        jak i *model*.
        """
        path = self._cache_path(question, model)
        if not self._is_fresh(path):
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

    def set(self, question: str, model: str, response: dict[str, Any]) -> None:
        """Zapisuje odpowiedź do cache."""
        path = self._cache_path(question, model)
        path.write_text(json.dumps(response, ensure_ascii=False), encoding="utf-8")

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _cache_path(self, question: str, model: str) -> Path:
        key = f"{model}:{question}"
        digest = sha256(key.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{digest}.json"

    def _is_fresh(self, path: Path) -> bool:
        if not path.exists() or self.ttl_seconds <= 0:
            return False
        age_seconds = time.time() - path.stat().st_mtime
        return age_seconds <= self.ttl_seconds
