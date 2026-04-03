"""Tests for GeminiClient - multi-model fallback, RPM/RPD limits, cache integration."""

import time
from unittest.mock import MagicMock

import pytest

from config.app_config_provider import AppConfigProvider
from infrastructure.gemini.cache import GeminiCache
from infrastructure.gemini.client import GeminiClient
from infrastructure.gemini.client import ModelConfig
from infrastructure.gemini.client import ModelState
from infrastructure.gemini.constants import DEFAULT_MODELS

# ---------------------------------------------------------------------------
# ModelConfig / _ModelState unit tests
# ---------------------------------------------------------------------------


def test_model_state_available_initially() -> None:
    state = ModelState(ModelConfig("m", requests_per_minute=5, requests_per_day=100))

    assert state.is_available(time.monotonic())


def test_model_state_rpm_exhausted() -> None:
    state = ModelState(ModelConfig("m", requests_per_minute=2, requests_per_day=100))

    now = time.monotonic()
    state.record_request(now)
    state.record_request(now)
    assert not state.is_available(now)


def test_model_state_rpd_exhausted() -> None:
    state = ModelState(ModelConfig("m", requests_per_minute=100, requests_per_day=2))

    now = time.monotonic()
    state.record_request(now)
    state.record_request(now)
    assert not state.is_available(now)


def test_model_state_rpm_window_expires() -> None:
    """After 60 s, RPM slots free up (sliding window)."""
    state = ModelState(ModelConfig("m", requests_per_minute=1, requests_per_day=100))

    past = time.monotonic() - 61.0  # 61 s ago
    state._rpm_timestamps.append(past)  # noqa: SLF001
    assert state.is_available(time.monotonic())


def test_model_state_rpd_window_expires() -> None:
    """After 24 h, RPD slots free up (sliding window)."""
    state = ModelState(ModelConfig("m", requests_per_minute=100, requests_per_day=1))

    past = time.monotonic() - 86401.0  # just over 24 h ago
    state._rpd_timestamps.append(past)  # noqa: SLF001
    assert state.is_available(time.monotonic())


def test_model_config_is_frozen() -> None:
    config = ModelConfig("m", requests_per_minute=5, requests_per_day=100)

    with pytest.raises(AttributeError):
        config.model = "other-model"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("model", "rpm", "rpd", "match"),
    [
        ("", 1, 1, "model"),
        ("   ", 1, 1, "model"),
        ("m", 0, 1, "requests_per_minute"),
        ("m", -1, 1, "requests_per_minute"),
        ("m", 1, 0, "requests_per_day"),
        ("m", 1, -1, "requests_per_day"),
    ],
)
def test_model_config_validation_boundaries(
    model: str,
    rpm: int,
    rpd: int,
    match: str,
) -> None:
    with pytest.raises(ValueError, match=match):
        ModelConfig(model, requests_per_minute=rpm, requests_per_day=rpd)


# ---------------------------------------------------------------------------
# GeminiClient constructor
# ---------------------------------------------------------------------------


def test_empty_api_key_raises() -> None:
    with pytest.raises(ValueError, match="API key"):
        GeminiClient(api_key="", models=[ModelConfig("m", 5, 100)])


def test_empty_models_list_raises() -> None:
    with pytest.raises(ValueError, match="Lista modeli nie może być pusta"):
        GeminiClient(api_key="key", models=[])


# ---------------------------------------------------------------------------
# GeminiClient.query - cache hit
# ---------------------------------------------------------------------------


def _make_client_with_mock_api(
    responses: list,
    *,
    models: list | None = None,
    cache: GeminiCache | None = None,
) -> tuple[GeminiClient, MagicMock]:
    """Helper creating GeminiClient with mocked _call_api side effects."""
    if models is None:
        models = [ModelConfig("model-a", requests_per_minute=10, requests_per_day=500)]
    client = GeminiClient(
        api_key="test-key",
        models=models,
        cache=cache or GeminiCache(cache_dir="gemini_test_cache_no_persist"),
    )
    # Replace _call_api with a side-effect iterator
    mock = MagicMock(side_effect=responses)
    client._call_api = mock  # noqa: SLF001
    return client, mock


def test_query_returns_api_result(tmp_path) -> None:
    cache = GeminiCache(cache_dir=tmp_path / "c")
    client, mock_api = _make_client_with_mock_api([{"answer": 1}], cache=cache)
    result = client.query("prompt")
    assert result == {"answer": 1}
    mock_api.assert_called_once()


def test_query_cache_hit_skips_api(tmp_path) -> None:
    cache = GeminiCache(cache_dir=tmp_path / "c")
    cache.set("prompt", "model-a", {"cached": True})
    client, mock_api = _make_client_with_mock_api([], cache=cache)
    result = client.query("prompt")
    assert result == {"cached": True}
    mock_api.assert_not_called()


def test_query_cache_hit_does_not_consume_rate_limits(tmp_path) -> None:
    cache = GeminiCache(cache_dir=tmp_path / "c")
    cache.set("prompt", "model-a", {"cached": True})
    client, _ = _make_client_with_mock_api([], cache=cache)

    state = client._model_states[0]  # noqa: SLF001
    rpm_before = len(state._rpm_timestamps)  # noqa: SLF001
    rpd_before = len(state._rpd_timestamps)  # noqa: SLF001

    result = client.query("prompt")

    assert result == {"cached": True}
    assert len(state._rpm_timestamps) == rpm_before  # noqa: SLF001
    assert len(state._rpd_timestamps) == rpd_before  # noqa: SLF001


def test_query_stores_result_in_cache(tmp_path) -> None:
    cache = GeminiCache(cache_dir=tmp_path / "c")
    client, _ = _make_client_with_mock_api([{"answer": 99}], cache=cache)
    client.query("prompt")
    assert cache.get("prompt", "model-a") == {"answer": 99}


# ---------------------------------------------------------------------------
# GeminiClient.query - model fallback on error
# ---------------------------------------------------------------------------


def test_query_falls_back_to_next_model_on_error(tmp_path) -> None:
    """When model-a raises RuntimeError, query retries with model-b."""
    cache = GeminiCache(cache_dir=tmp_path / "c")
    models = [
        ModelConfig("model-a", requests_per_minute=10, requests_per_day=500),
        ModelConfig("model-b", requests_per_minute=10, requests_per_day=500),
    ]
    client = GeminiClient(api_key="key", models=models, cache=cache)

    call_log: list[str] = []

    def fake_call_api(_prompt, *, model, response_mime_type):
        del response_mime_type
        call_log.append(model)
        if model == "model-a":
            msg = "API error from model-a"
            raise RuntimeError(msg)
        return {"result": "ok"}

    client._call_api = fake_call_api  # noqa: SLF001
    result = client.query("prompt")

    assert result == {"result": "ok"}
    assert call_log == ["model-a", "model-b"]


def test_query_falls_back_to_next_model_on_non_runtime_error(tmp_path) -> None:
    """Any API/transport exception should trigger fallback to the next model."""
    cache = GeminiCache(cache_dir=tmp_path / "c")
    models = [
        ModelConfig("model-a", requests_per_minute=10, requests_per_day=500),
        ModelConfig("model-b", requests_per_minute=10, requests_per_day=500),
    ]
    client = GeminiClient(api_key="key", models=models, cache=cache)

    call_log: list[str] = []

    def fake_call_api(_prompt, *, model, response_mime_type):
        del response_mime_type
        call_log.append(model)
        if model == "model-a":
            msg = "transport timeout"
            raise TimeoutError(msg)
        return {"result": "ok"}

    client._call_api = fake_call_api  # noqa: SLF001
    result = client.query("prompt")

    assert result == {"result": "ok"}
    assert call_log == ["model-a", "model-b"]


def test_query_after_fallback_returns_to_primary_model_for_next_prompt(
    tmp_path,
) -> None:
    """Fallback is per prompt: next prompt starts again from the first model."""
    cache = GeminiCache(cache_dir=tmp_path / "c")
    models = [
        ModelConfig("model-a", requests_per_minute=10, requests_per_day=500),
        ModelConfig("model-b", requests_per_minute=10, requests_per_day=500),
    ]
    client = GeminiClient(api_key="key", models=models, cache=cache)

    call_log: list[tuple[str, str]] = []

    def fake_call_api(prompt, *, model, response_mime_type):
        del response_mime_type
        call_log.append((prompt, model))
        if prompt == "prompt-1" and model == "model-a":
            msg = "temporary timeout"
            raise TimeoutError(msg)
        return {"result": f"ok-{prompt}-{model}"}

    client._call_api = fake_call_api  # noqa: SLF001

    first = client.query("prompt-1")
    second = client.query("prompt-2")

    assert first == {"result": "ok-prompt-1-model-b"}
    assert second == {"result": "ok-prompt-2-model-a"}
    assert call_log == [
        ("prompt-1", "model-a"),
        ("prompt-1", "model-b"),
        ("prompt-2", "model-a"),
    ]


def test_query_raises_when_all_models_exhausted(tmp_path) -> None:
    """RuntimeError is raised when every model in the list returns an error."""
    cache = GeminiCache(cache_dir=tmp_path / "c")
    models = [
        ModelConfig("model-a", requests_per_minute=10, requests_per_day=500),
        ModelConfig("model-b", requests_per_minute=10, requests_per_day=500),
    ]
    client = GeminiClient(api_key="key", models=models, cache=cache)
    client._call_api = MagicMock(side_effect=RuntimeError("always fails"))  # noqa: SLF001

    with pytest.raises(RuntimeError, match="wyczerpane"):
        client.query("prompt")


# ---------------------------------------------------------------------------
# GeminiClient.query - RPM/RPD fallback
# ---------------------------------------------------------------------------


def test_query_skips_rpm_exhausted_model(tmp_path) -> None:
    """When model-a is at RPM limit, the query uses model-b."""

    cache = GeminiCache(cache_dir=tmp_path / "c")
    models = [
        ModelConfig("model-a", requests_per_minute=1, requests_per_day=500),
        ModelConfig("model-b", requests_per_minute=10, requests_per_day=500),
    ]
    client = GeminiClient(api_key="key", models=models, cache=cache)
    # Saturate model-a RPM
    now = time.monotonic()
    client._model_states[0]._rpm_timestamps.append(now)  # noqa: SLF001

    call_log: list[str] = []

    def fake_call_api(_prompt, *, model, response_mime_type):
        del response_mime_type
        call_log.append(model)
        return {"ok": True}

    client._call_api = fake_call_api  # noqa: SLF001
    result = client.query("p")

    assert result == {"ok": True}
    assert "model-b" in call_log
    assert "model-a" not in call_log


def test_query_raises_when_all_models_at_rpm_limit(tmp_path) -> None:
    """RuntimeError when every model has hit its RPM limit and no fallback remains."""

    cache = GeminiCache(cache_dir=tmp_path / "c")
    models = [
        ModelConfig("model-a", requests_per_minute=1, requests_per_day=500),
    ]
    client = GeminiClient(api_key="key", models=models, cache=cache)
    now = time.monotonic()
    client._model_states[0]._rpm_timestamps.append(now)  # noqa: SLF001

    with pytest.raises(RuntimeError, match="wyczerpane"):
        client.query("prompt")


# ---------------------------------------------------------------------------
# GeminiClient.from_key_file
# ---------------------------------------------------------------------------


def test_from_key_file_raises_for_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        GeminiClient.from_key_file("nonexistent_gemini_key_xyz.txt")


def test_from_key_file_uses_default_models(tmp_path) -> None:
    key_file = tmp_path / "key.txt"
    key_file.write_text("my-api-key", encoding="utf-8")
    client = GeminiClient.from_key_file(key_file)
    assert len(client._model_states) > 0  # noqa: SLF001


def test_from_config_provider_uses_provider_values(tmp_path) -> None:
    expected_timeout = 41
    key_file = tmp_path / "key.txt"
    key_file.write_text("my-provider-key", encoding="utf-8")
    provider = AppConfigProvider(
        env={
            "GEMINI_API_KEY_FILE": str(key_file),
            "GEMINI_TIMEOUT_SECONDS": str(expected_timeout),
        },
        project_root=tmp_path,
    )

    client = GeminiClient.from_config_provider(provider)

    assert len(client._model_states) > 0  # noqa: SLF001
    assert client._transport._timeout == expected_timeout  # noqa: SLF001
    assert client._model_states[0].model == "gemini-3-flash-preview"  # noqa: SLF001
    assert client._model_states[0].model == DEFAULT_MODELS[0].model  # noqa: SLF001


def test_from_key_file_accepts_custom_models(tmp_path) -> None:
    key_file = tmp_path / "key.txt"
    key_file.write_text("my-api-key", encoding="utf-8")
    custom = [ModelConfig("custom-model", requests_per_minute=5, requests_per_day=100)]
    client = GeminiClient.from_key_file(key_file, models=custom)
    assert client._model_states[0].model == "custom-model"  # noqa: SLF001
