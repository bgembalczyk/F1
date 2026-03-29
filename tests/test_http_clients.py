# ruff: noqa: E501, PLR2004, RUF001, RUF002, RUF003, SLF001, ARG001, ARG002, N802, B017, PT011, PT017, E402, PT001, PLC0415, RUF100
import threading
import time
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler
from http.server import ThreadingHTTPServer

import pytest

from infrastructure.http_client.caching.file import FileCache
from infrastructure.http_client.caching.wiki import WikipediaCachePolicy
from infrastructure.http_client.clients.urllib_http import UrllibHttpClient
from infrastructure.http_client.config import HttpClientConfig
from infrastructure.http_client.policies.default_retry import DefaultRetryPolicy
from infrastructure.http_client.requests_shim.session import Session
from scrapers.base.options import HttpPolicy
from scrapers.base.options import ScraperOptions


class _StubHandler(BaseHTTPRequestHandler):
    retry_count = 0
    delay_seconds = 0.0
    last_header = ""

    def do_GET(self):
        if self.path == "/flaky":
            type(self).retry_count += 1
            if type(self).retry_count < 2:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b"fail")
                return
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")
            return

        if self.path == "/headers":
            type(self).last_header = self.headers.get("X-Test-Header", "")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(type(self).last_header.encode("utf-8"))
            return

        if self.path == "/json":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status": "ok", "value": 1}')
            return

        if self.path == "/slow":
            time.sleep(type(self).delay_seconds)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"slow")
            return

        if self.path == "/text":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"plain-text")
            return

        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"not-found")

    def log_message(self, *args, **kwargs):  # pragma: no cover - tłumienie logów
        return


@pytest.fixture(scope="module")
def http_server():
    server = ThreadingHTTPServer(("localhost", 0), _StubHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://{server.server_address[0]}:{server.server_address[1]}"

    yield base_url, _StubHandler

    server.shutdown()
    thread.join()


def _client_with_config(client_cls, **config_kwargs):
    """
    Helper: buduje klienta przez HttpClientConfig (nowy styl),
    ale zostawia testom możliwość podania dowolnych pól configu.
    """
    cfg = HttpClientConfig(**config_kwargs)
    return client_cls(config=cfg)


CLIENT_FACTORIES: list[tuple[str, Callable[..., object]]] = [
    (
        "urllib",
        lambda **kwargs: _client_with_config(
            UrllibHttpClient,
            backoff_seconds=0.01,
            **kwargs,
        ),
    ),
]


@pytest.mark.parametrize(("name", "factory"), CLIENT_FACTORIES)
def test_retries_on_server_errors(name, factory, http_server):
    base_url, handler = http_server
    handler.retry_count = 0

    client = factory(retries=1, timeout=1)
    response = client.get(f"{base_url}/flaky")

    assert response.status_code == 200
    assert handler.retry_count == 2


@pytest.mark.parametrize(("name", "factory"), CLIENT_FACTORIES)
def test_custom_headers_are_forwarded(name, factory, http_server):
    base_url, handler = http_server
    handler.last_header = ""

    client = factory()
    response = client.get(f"{base_url}/headers", headers={"X-Test-Header": "demo"})

    assert response.text == "demo"
    assert handler.last_header == "demo"


def test_header_merge_priority_client_over_session(http_server):
    base_url, handler = http_server
    handler.last_header = ""

    session = Session()
    session.headers["X-Test-Header"] = "from-session"
    client = UrllibHttpClient(
        session=session,
        config=HttpClientConfig(headers={"X-Test-Header": "from-client"}),
    )

    response = client.get(f"{base_url}/headers")

    assert response.text == "from-client"
    assert handler.last_header == "from-client"


def test_header_merge_priority_request_over_client_and_session(http_server):
    base_url, handler = http_server
    handler.last_header = ""

    session = Session()
    session.headers["X-Test-Header"] = "from-session"
    client = UrllibHttpClient(
        session=session,
        config=HttpClientConfig(headers={"X-Test-Header": "from-client"}),
    )

    response = client.get(
        f"{base_url}/headers",
        headers={"X-Test-Header": "from-request"},
    )

    assert response.text == "from-request"
    assert handler.last_header == "from-request"


@pytest.mark.parametrize(("name", "factory"), CLIENT_FACTORIES)
def test_timeouts_are_respected(name, factory, http_server):
    base_url, handler = http_server
    handler.delay_seconds = 0.2

    client = factory(timeout=0.05, retries=0)

    with pytest.raises(Exception):
        client.get(f"{base_url}/slow")


@pytest.mark.parametrize(("name", "factory"), CLIENT_FACTORIES)
def test_get_text_contract(name, factory, http_server):
    base_url, _handler = http_server

    client = factory()
    payload = client.get_text(f"{base_url}/text")

    assert payload == "plain-text"
    assert isinstance(payload, str)


@pytest.mark.parametrize(("name", "factory"), CLIENT_FACTORIES)
def test_get_json_contract(name, factory, http_server):
    base_url, _handler = http_server

    client = factory()
    payload = client.get_json(f"{base_url}/json")

    assert payload == {"status": "ok", "value": 1}


def test_wikipedia_cache_policy_hit_and_miss(tmp_path):
    cache = WikipediaCachePolicy(FileCache(cache_dir=tmp_path, ttl_seconds=60))
    url = "https://en.wikipedia.org/wiki/Formula_One"
    other_url = "https://example.com"

    assert cache.get(url) is None
    cache.set(url, "cached")
    assert cache.get(url) == "cached"

    cache.set(other_url, "skip")
    assert cache.get(other_url) is None


def test_default_retry_policy_for_statuses():
    policy = DefaultRetryPolicy(retries=1, backoff_seconds=0.01)

    class _Response:
        def __init__(self, status_code, text=""):
            self.status_code = status_code
            self.text = text

    assert (
        policy.should_retry(response=_Response(429), exception=None, attempt=0) is True
    )
    assert (
        policy.should_retry(response=_Response(500), exception=None, attempt=0) is True
    )
    assert (
        policy.should_retry(response=_Response(404), exception=None, attempt=0) is False
    )
    assert (
        policy.should_retry(
            response=_Response(403, text="Please respect our robot policy"),
            exception=None,
            attempt=0,
        )
        is True
    )


class _DummyHttpClient:
    def get_text(self, url: str, *, timeout: int | None = None) -> str:
        return f"{url}::{timeout}"


def test_http_policy_shared_between_scraper_options_and_fetchers():
    policy = HttpPolicy(timeout=5, retries=1, cache=None)
    http_client = _DummyHttpClient()

    options = ScraperOptions(policy=policy, http_client=http_client)
    fetcher = options.with_fetcher()

    sub_options = ScraperOptions(
        policy=options.policy,
        http_client=options.http_client,
        source_adapter=fetcher,
    )
    sub_fetcher = sub_options.with_fetcher()

    assert fetcher.policy is policy
    assert sub_fetcher is fetcher
    assert sub_fetcher.policy is policy
