import os
import time
from hashlib import sha256
from pathlib import Path
from typing import Any

from infrastructure.cache.file_ttl_cache import FileTtlCache
from infrastructure.cache.file_ttl_cache import FileTtlCacheAdapter
from infrastructure.cache.file_ttl_cache import GeminiJsonFileCacheAdapter
from infrastructure.cache.file_ttl_cache import HttpResponseFileCacheAdapter
from infrastructure.gemini.cache import GeminiCache
from infrastructure.http_client.caching.file import FileCache


class _IntAdapter(FileTtlCacheAdapter[int]):
    extension = ".txt"

    def serialize(self, value: int) -> str:
        return str(value)

    def deserialize(self, raw_text: str) -> int:
        return int(raw_text)


def test_file_ttl_cache_roundtrip(tmp_path: Path) -> None:
    cache = FileTtlCache[int](
        cache_dir=tmp_path / "cache",
        ttl_seconds=60,
        adapter=_IntAdapter(),
    )

    cache.set("key-1", 123)

    assert cache.get("key-1") == 123


def test_file_ttl_cache_ttl_expired(tmp_path: Path) -> None:
    cache = FileTtlCache[int](
        cache_dir=tmp_path / "cache",
        ttl_seconds=1,
        adapter=_IntAdapter(),
    )

    cache.set("key-1", 123)
    cache_file = next((tmp_path / "cache").glob("*.txt"))
    old_ts = time.time() - 120
    os.utime(cache_file, (old_ts, old_ts))

    assert cache.get("key-1") is None


def test_file_ttl_cache_zero_ttl_disables_reads(tmp_path: Path) -> None:
    cache = FileTtlCache[int](
        cache_dir=tmp_path / "cache",
        ttl_seconds=0,
        adapter=_IntAdapter(),
    )

    cache.set("key-1", 123)

    assert cache.get("key-1") is None


def test_file_ttl_cache_bad_payload_returns_none(tmp_path: Path) -> None:
    cache = FileTtlCache[int](
        cache_dir=tmp_path / "cache",
        ttl_seconds=60,
        adapter=_IntAdapter(),
    )

    digest = sha256(b"bad-key").hexdigest()
    cache_file = tmp_path / "cache" / f"{digest}.txt"
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text("not-int", encoding="utf-8")

    assert cache.get("bad-key") is None


def test_http_adapter_serializes_as_plain_text() -> None:
    adapter = HttpResponseFileCacheAdapter()

    assert adapter.extension == ".html"
    assert adapter.serialize("abc") == "abc"
    assert adapter.deserialize("abc") == "abc"


def test_gemini_json_adapter_roundtrip() -> None:
    adapter = GeminiJsonFileCacheAdapter()
    payload: dict[str, Any] = {"value": 1, "nested": {"x": True}}

    raw = adapter.serialize(payload)

    assert adapter.extension == ".json"
    assert adapter.deserialize(raw) == payload


def test_file_cache_is_thin_adapter_over_file_ttl_cache(tmp_path: Path) -> None:
    cache = FileCache(cache_dir=tmp_path, ttl_seconds=60)

    cache.set("https://example.com", "<html>ok</html>")

    assert cache.get("https://example.com") == "<html>ok</html>"


def test_gemini_cache_is_thin_adapter_over_file_ttl_cache(tmp_path: Path) -> None:
    cache = GeminiCache(cache_dir=tmp_path / "gemini", ttl_seconds=60)

    cache.set("question", "model-a", {"answer": 7})

    assert cache.get("question", "model-a") == {"answer": 7}
    assert cache.get("question", "model-b") is None
