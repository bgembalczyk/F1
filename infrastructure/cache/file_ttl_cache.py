import json
import time
from hashlib import sha256
from pathlib import Path
from typing import Any
from typing import Generic
from typing import Protocol
from typing import TypeVar

T = TypeVar("T")


class FileTtlCacheAdapter(Protocol[T]):
    """Adapter serializacji wartości cache do/z tekstu."""

    extension: str

    def serialize(self, value: T) -> str:
        """Serializuje wartość do postaci tekstowej."""

    def deserialize(self, raw_text: str) -> T:
        """Deserializuje tekst do docelowego typu."""


class HttpResponseFileCacheAdapter:
    """Adapter cache dla tekstowej odpowiedzi HTTP."""

    extension = ".html"

    def serialize(self, value: str) -> str:
        return value

    def deserialize(self, raw_text: str) -> str:
        return raw_text


class GeminiJsonFileCacheAdapter:
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


class FileTtlCache(Generic[T]):
    """Plikowy cache z TTL oparty o klucze tekstowe."""

    def __init__(
        self,
        *,
        cache_dir: Path | str,
        ttl_seconds: int,
        adapter: FileTtlCacheAdapter[T],
    ) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = max(0, int(ttl_seconds))
        self._adapter = adapter

    def get(self, key: str) -> T | None:
        path = self._cache_path(key)
        if not self._is_fresh(path):
            return None
        try:
            raw_text = path.read_text(encoding="utf-8")
            return self._adapter.deserialize(raw_text)
        except (OSError, ValueError, json.JSONDecodeError):
            return None

    def set(self, key: str, value: T) -> None:
        path = self._cache_path(key)
        raw_text = self._adapter.serialize(value)
        path.write_text(raw_text, encoding="utf-8")

    def _cache_path(self, key: str) -> Path:
        digest = sha256(key.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{digest}{self._adapter.extension}"

    def _is_fresh(self, path: Path) -> bool:
        if not path.exists() or self.ttl_seconds <= 0:
            return False
        age_seconds = time.time() - path.stat().st_mtime
        return age_seconds <= self.ttl_seconds
