from __future__ import annotations

from collections.abc import Mapping

from bs4 import BeautifulSoup

from infrastructure.http_client.interfaces.http_client_protocol import HttpClientProtocol
from infrastructure.http_client.interfaces.http_client_protocol import JsonValue
from infrastructure.http_client.interfaces.http_response_protocol import (
    HttpResponseProtocol,
)
from infrastructure.http_client.interfaces.session_protocol import SessionProtocol
from infrastructure.http_client.policies.response_cache import TextCacheProtocol
from models.serializers import SerializerProtocol
from scrapers.base.errors import ScraperParseError
from scrapers.base.parsers.soup import SoupParser


class _StubSoupParser:
    def parse(self, soup: BeautifulSoup) -> dict[str, str]:
        return {"title": soup.title.get_text(strip=True) if soup.title else ""}


class _StubSerializer:
    def serialize(self, value: Mapping[str, object]) -> dict[str, object]:
        return dict(value)


class _StubTextCache:
    def __init__(self) -> None:
        self._storage: dict[str, str] = {}

    def get(self, url: str) -> str | None:
        return self._storage.get(url)

    def set(self, url: str, text: str) -> None:
        self._storage[url] = text


class _StubResponse:
    def __init__(self, *, text: str = "", status_code: int = 200) -> None:
        self.text = text
        self.status_code = status_code
        self.headers: Mapping[str, str] = {}

    def raise_for_status(self) -> None:
        return None

    def json(self) -> object:
        return {"ok": True}


class _StubSession:
    headers: Mapping[str, str] = {}

    def get(
        self,
        url: str,
        headers: Mapping[str, str] | None = None,
        timeout: int | None = None,
    ) -> HttpResponseProtocol:
        _ = (url, headers, timeout)
        return _StubResponse(text="{}")


class _StubHttpClient:
    session: SessionProtocol

    def __init__(self) -> None:
        self.session = _StubSession()

    def get(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        timeout: int | None = None,
    ) -> HttpResponseProtocol:
        _ = (url, headers, timeout)
        return _StubResponse(text='{"ok": true}')

    def get_text(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        timeout: int | None = None,
    ) -> str:
        _ = (url, headers, timeout)
        return '{"ok": true}'

    def get_json(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        timeout: int | None = None,
    ) -> JsonValue:
        _ = (url, headers, timeout)
        return {"ok": True}


def test_parser_protocol_contract() -> None:
    assert isinstance(_StubSoupParser(), SoupParser)


def test_serializer_protocol_contract() -> None:
    assert isinstance(_StubSerializer(), SerializerProtocol)


def test_text_cache_protocol_contract() -> None:
    cache = _StubTextCache()
    cache.set("a", "b")
    assert cache.get("a") == "b"
    assert isinstance(cache, TextCacheProtocol)


def test_http_protocol_contracts() -> None:
    client = _StubHttpClient()
    assert isinstance(client.session, SessionProtocol)
    assert isinstance(client.get("https://example.com"), HttpResponseProtocol)
    assert isinstance(client, HttpClientProtocol)


def test_scraper_error_payload_contract() -> None:
    error = ScraperParseError(
        "parse failed",
        url="https://example.com/wiki",
        section_id="results",
        parser_name="SampleParser",
        run_id="run-1",
    )
    payload = error.to_payload()
    assert payload["category"] == "parse"
    assert payload["behavior"] == "hard"
    assert payload["section_id"] == "results"
