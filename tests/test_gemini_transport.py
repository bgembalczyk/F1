import io
import ssl
import urllib.error

import pytest

from infrastructure.gemini.transport import GeminiTransport


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
        timeout=5,
        ssl_context=ssl.create_default_context(),
    )


def test_generate_returns_decoded_response(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = _transport()

    def fake_urlopen(*_args, **_kwargs):
        return _DummyResponse('{"candidates": []}')

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    assert transport.generate("p", model="m", response_mime_type="application/json") == {
        "candidates": [],
    }


def test_generate_wraps_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = _transport()

    def fake_urlopen(*_args, **_kwargs):
        raise urllib.error.HTTPError(
            url="https://x",
            code=429,
            msg="Too Many Requests",
            hdrs=None,
            fp=io.BytesIO(b"quota"),
        )

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    with pytest.raises(RuntimeError, match="HTTP 429"):
        transport.generate("p", model="m", response_mime_type="application/json")


def test_generate_raises_for_invalid_json(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = _transport()

    def fake_urlopen(*_args, **_kwargs):
        return _DummyResponse("not-json")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    with pytest.raises(RuntimeError, match="niepoprawny JSON"):
        transport.generate("p", model="m", response_mime_type="application/json")
