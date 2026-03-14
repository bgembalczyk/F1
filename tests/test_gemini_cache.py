"""Tests for GeminiCache – model is part of the cache key."""

import time
from pathlib import Path

from infrastructure.gemini.cache import GeminiCache


def _make_cache(tmp_path: Path, ttl: int = 3600) -> GeminiCache:
    return GeminiCache(cache_dir=tmp_path / "gemini_cache", ttl_seconds=ttl)


def test_set_and_get_returns_stored_value(tmp_path: Path) -> None:
    cache = _make_cache(tmp_path)
    cache.set("question", "model-a", {"answer": 42})
    assert cache.get("question", "model-a") == {"answer": 42}


def test_get_returns_none_for_missing_key(tmp_path: Path) -> None:
    cache = _make_cache(tmp_path)
    assert cache.get("missing question", "model-a") is None


def test_model_is_part_of_cache_key(tmp_path: Path) -> None:
    """Same prompt with different models yields separate cache entries."""
    cache = _make_cache(tmp_path)
    cache.set("question", "model-a", {"answer": 1})
    cache.set("question", "model-b", {"answer": 2})

    assert cache.get("question", "model-a") == {"answer": 1}
    assert cache.get("question", "model-b") == {"answer": 2}


def test_wrong_model_returns_none(tmp_path: Path) -> None:
    """Cache miss when prompt matches but model does not."""
    cache = _make_cache(tmp_path)
    cache.set("question", "model-a", {"answer": 1})
    assert cache.get("question", "model-b") is None


def test_expired_entry_returns_none(tmp_path: Path) -> None:
    cache = _make_cache(tmp_path, ttl=1)
    cache.set("q", "model-a", {"x": 1})
    time.sleep(1.1)
    assert cache.get("q", "model-a") is None


def test_zero_ttl_always_returns_none(tmp_path: Path) -> None:
    cache = _make_cache(tmp_path, ttl=0)
    cache.set("q", "model-a", {"x": 1})
    assert cache.get("q", "model-a") is None


def test_corrupted_cache_file_returns_none(tmp_path: Path) -> None:
    cache = _make_cache(tmp_path)
    cache.set("q", "model-a", {"x": 1})
    # Corrupt the cache file
    from hashlib import sha256

    digest = sha256(b"model-a:q").hexdigest()
    cache_file = tmp_path / "gemini_cache" / f"{digest}.json"
    cache_file.write_text("not valid json", encoding="utf-8")
    assert cache.get("q", "model-a") is None
