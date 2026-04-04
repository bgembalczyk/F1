import importlib
import io
import ssl
import sys
import types
import urllib.error
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest


def _install_scrapers_pkg_stub() -> None:
    if "scrapers" in sys.modules:
        return
    pkg = types.ModuleType("scrapers")
    pkg.__path__ = [str(Path(__file__).resolve().parents[1] / "scrapers")]
    sys.modules["scrapers"] = pkg


_install_scrapers_pkg_stub()

from infrastructure.gemini.cache import GeminiCache  # noqa: E402
from infrastructure.gemini.cache_service import GeminiCacheService  # noqa: E402
from infrastructure.gemini.client import GeminiClient  # noqa: E402
from infrastructure.gemini.model_config import ModelConfig  # noqa: E402
from infrastructure.gemini.model_selector import ModelSelector  # noqa: E402
from infrastructure.gemini.orchestration import GeminiOrchestrationService  # noqa: E402
from infrastructure.gemini.transport import GeminiTransport  # noqa: E402
from scrapers.base.errors import PipelineError  # noqa: E402
from scrapers.base.errors import SourceParseError  # noqa: E402
from scrapers.base.errors import TransportError  # noqa: E402


def test_package_exports_and_lazy_client_import() -> None:
    module = importlib.import_module("infrastructure.gemini")

    assert "GeminiClient" in module.__all__
    assert module.ModelConfig is ModelConfig
    assert module.DEFAULT_TIMEOUT > 0

    assert module.GeminiClient is GeminiClient


def test_package_unknown_attribute_raises_attribute_error() -> None:
    module = importlib.import_module("infrastructure.gemini")

    with pytest.raises(AttributeError, match="has no attribute"):
        _ = module.NOT_EXISTS


def test_cache_service_emits_deprecation_and_delegates(tmp_path: Path) -> None:
    cache = GeminiCache(cache_dir=tmp_path / "cache")

    with pytest.deprecated_call(match="GeminiCacheService jest przestarzały"):
        service = GeminiCacheService(cache)

    assert service.cache is cache
    assert service.get("prompt", "m") is None

    payload = {"ok": True}
    service.set("prompt", "m", payload)
    assert service.get("prompt", "m") == payload


def test_model_selector_pick_model_with_exclude_and_empty_models_error() -> None:
    with pytest.raises(ValueError, match="Lista modeli nie może być pusta"):
        ModelSelector([])

    selector = ModelSelector(
        [
            ModelConfig("m1", requests_per_minute=1, requests_per_day=10),
            ModelConfig("m2", requests_per_minute=1, requests_per_day=10),
        ],
    )

    assert selector.pick_model() == "m1"
    assert selector.pick_model(exclude={"m1"}) == "m2"


def test_model_selector_try_record_request_respects_limits() -> None:
    selector = ModelSelector(
        [ModelConfig("m", requests_per_minute=1, requests_per_day=10)],
    )

    assert selector.try_record_request("m")
    assert not selector.try_record_request("m")
    assert not selector.try_record_request("unknown")


def test_orchestration_cache_hit_and_miss(tmp_path: Path) -> None:
    cache = GeminiCache(cache_dir=tmp_path / "cache")
    selector = ModelSelector(
        [ModelConfig("m", requests_per_minute=5, requests_per_day=50)],
    )
    service = GeminiOrchestrationService(model_selector=selector, cache=cache)

    cache.set("p-hit", "m", {"cached": True})
    call_api = Mock(return_value={"fresh": True})

    assert service.run("p-hit", call_api=call_api) == {"cached": True}
    call_api.assert_not_called()

    assert service.run("p-miss", call_api=call_api) == {"fresh": True}
    call_api.assert_called_once_with("m")
    assert cache.get("p-miss", "m") == {"fresh": True}


def test_orchestration_maps_transport_error_and_falls_back(tmp_path: Path) -> None:
    cache = GeminiCache(cache_dir=tmp_path / "cache")
    selector = ModelSelector(
        [
            ModelConfig("m1", requests_per_minute=5, requests_per_day=50),
            ModelConfig("m2", requests_per_minute=5, requests_per_day=50),
        ],
    )
    service = GeminiOrchestrationService(model_selector=selector, cache=cache)

    seen: list[str] = []

    def call_api(model: str) -> dict[str, object]:
        seen.append(model)
        if model == "m1":
            msg = "socket timeout"
            raise TimeoutError(msg)
        return {"ok": model}

    assert service.run("prompt", call_api=call_api) == {"ok": "m2"}
    assert seen == ["m1", "m2"]


def test_orchestration_raises_models_exhausted_when_all_models_fail(
    tmp_path: Path,
) -> None:
    cache = GeminiCache(cache_dir=tmp_path / "cache")
    selector = ModelSelector(
        [
            ModelConfig("m1", requests_per_minute=5, requests_per_day=50),
            ModelConfig("m2", requests_per_minute=5, requests_per_day=50),
        ],
    )
    service = GeminiOrchestrationService(model_selector=selector, cache=cache)

    def call_api(_model: str) -> dict[str, object]:
        raise TransportError(message="boom")

    with pytest.raises(PipelineError, match="modele Gemini są wyczerpane") as exc_info:
        service.run("prompt", call_api=call_api)

    assert exc_info.value.code == "gemini.models_exhausted"


def test_client_from_config_provider_uses_config_timeout() -> None:
    _expected_timeout = 17
    app_config = SimpleNamespace(
        gemini=SimpleNamespace(api_key="k", timeout_seconds=_expected_timeout),
    )
    provider = Mock()
    provider.get.return_value = app_config

    client = GeminiClient.from_config_provider(provider)

    assert isinstance(client, GeminiClient)
    assert client._transport._timeout == _expected_timeout  # noqa: SLF001


def test_client_call_api_maps_empty_response_to_source_parse_error(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    cache = GeminiCache(cache_dir=tmp_path / "cache")
    client = GeminiClient(
        api_key="k",
        models=[ModelConfig("m", requests_per_minute=5, requests_per_day=50)],
        cache=cache,
    )

    monkeypatch.setattr(
        client._transport,  # noqa: SLF001
        "generate",
        lambda *_args, **_kwargs: {"candidates": []},
    )

    with pytest.raises(SourceParseError, match="nie zwróciło pola"):
        client._call_api(  # noqa: SLF001
            "prompt",
            model="m",
            response_mime_type="application/json",
        )


class _DummyResponse:
    def __init__(self, body: str) -> None:
        self._body = body.encode("utf-8")

    def read(self) -> bytes:
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


def _transport() -> GeminiTransport:
    return GeminiTransport(
        api_key="test-key",
        timeout=3,
        ssl_context=ssl.create_default_context(),
    )


def test_transport_success_and_error_mapping(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = _transport()

    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda *_args, **_kwargs: _DummyResponse('{"candidates": []}'),
    )
    assert transport.generate(
        "p",
        model="m",
        response_mime_type="application/json",
    ) == {
        "candidates": [],
    }

    def raise_http(*_args, **_kwargs):
        raise urllib.error.HTTPError(
            url="https://x",
            code=503,
            msg="down",
            hdrs=None,
            fp=io.BytesIO(b"e"),
        )

    monkeypatch.setattr("urllib.request.urlopen", raise_http)
    with pytest.raises(TransportError, match="HTTP 503"):
        transport.generate("p", model="m", response_mime_type="application/json")

    def raise_url(*_args, **_kwargs):
        msg = "timeout"
        raise urllib.error.URLError(msg)

    monkeypatch.setattr("urllib.request.urlopen", raise_url)
    with pytest.raises(TransportError, match="connection error"):
        transport.generate("p", model="m", response_mime_type="application/json")


def test_transport_rejects_non_https_and_invalid_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transport = _transport()

    monkeypatch.setattr(
        "infrastructure.gemini.transport.API_URL_TEMPLATE",
        "http://example.com/{model}?key={api_key}",
    )
    with pytest.raises(TransportError, match="schematu https"):
        transport.generate("p", model="m", response_mime_type="application/json")

    monkeypatch.setattr(
        "infrastructure.gemini.transport.API_URL_TEMPLATE",
        "https://example.com/{model}?key={api_key}",
    )
    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda *_a, **_k: _DummyResponse("not-json"),
    )
    with pytest.raises(TransportError, match="niepoprawny JSON"):
        transport.generate("p", model="m", response_mime_type="application/json")
