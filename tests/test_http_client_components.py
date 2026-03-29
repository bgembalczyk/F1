# ruff: noqa: E501, PLR2004, SLF001
from dataclasses import dataclass

from infrastructure.http_client.caching.file import FileCache
from infrastructure.http_client.components.header_resolver import HeaderResolver
from infrastructure.http_client.components.request_executor import RequestExecutor
from infrastructure.http_client.components.response_cache_service import ResponseCacheService
from infrastructure.http_client.config import HttpClientConfig
from infrastructure.http_client.factories.default_http_policy_factory import (
    DefaultHttpPolicyFactory,
)
from infrastructure.http_client.policies.default_retry import DefaultRetryPolicy


class DummyRequestError(Exception):
    pass


@dataclass
class _DummyResponse:
    status_code: int
    text: str = ""

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise DummyRequestError(f"http {self.status_code}")


class _RetryOnServerErrorPolicy:
    @property
    def max_retries(self) -> int:
        return 1

    def should_retry(self, *, response, exception, attempt: int) -> bool:
        if exception is not None:
            return True
        if response is not None and getattr(response, "status_code", 0) >= 500:
            return True
        return False

    def backoff_seconds(self, attempt: int) -> float:
        return 0.0


class _NoopRateLimiter:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def wait(self, url: str) -> None:
        self.calls.append(url)


class _MemoryCache:
    def __init__(self) -> None:
        self.storage: dict[str, str] = {}

    def get(self, url: str) -> str | None:
        return self.storage.get(url)

    def set(self, url: str, text: str) -> None:
        self.storage[url] = text


def test_header_resolver_merges_default_and_request_headers() -> None:
    resolver = HeaderResolver(default_headers={"User-Agent": "ua", "X-Base": "1"})

    result = resolver.resolve({"X-Base": "2", "X-Req": "3"})

    assert result == {"User-Agent": "ua", "X-Base": "2", "X-Req": "3"}


def test_response_cache_service_reads_and_writes_cache() -> None:
    cache = _MemoryCache()
    service = ResponseCacheService(cache=cache)
    calls = {"count": 0}

    def fetch_text() -> str:
        calls["count"] += 1
        return "payload"

    first = service.get_text("https://en.wikipedia.org/wiki/F1", fetch_text)
    second = service.get_text("https://en.wikipedia.org/wiki/F1", fetch_text)

    assert first == "payload"
    assert second == "payload"
    assert calls["count"] == 1


def test_request_executor_retries_after_retryable_status() -> None:
    rate_limiter = _NoopRateLimiter()
    policy = _RetryOnServerErrorPolicy()
    executor = RequestExecutor(retry_policy=policy, rate_limiter=rate_limiter)

    calls = {"count": 0}

    def request_func(url: str, *, headers: dict[str, str], timeout: int):
        calls["count"] += 1
        if calls["count"] == 1:
            return _DummyResponse(status_code=500)
        return _DummyResponse(status_code=200, text="ok")

    response = executor.execute(
        url="https://en.wikipedia.org/wiki/F1",
        headers={"X": "1"},
        timeout=3,
        request_func=request_func,
        request_error_contract=DummyRequestError,
    )

    assert response.status_code == 200
    assert calls["count"] == 2
    assert len(rate_limiter.calls) == 2


def test_request_executor_raises_after_exhausted_retryable_exceptions() -> None:
    rate_limiter = _NoopRateLimiter()
    policy = _RetryOnServerErrorPolicy()
    executor = RequestExecutor(retry_policy=policy, rate_limiter=rate_limiter)

    def request_func(url: str, *, headers: dict[str, str], timeout: int):
        raise DummyRequestError("network")

    try:
        executor.execute(
            url="https://en.wikipedia.org/wiki/F1",
            headers={"X": "1"},
            timeout=3,
            request_func=request_func,
            request_error_contract=DummyRequestError,
        )
    except DummyRequestError:
        pass
    else:
        msg = "Expected DummyRequestError"
        raise AssertionError(msg)

    assert len(rate_limiter.calls) == 2


def test_default_http_policy_factory_builds_default_components(tmp_path) -> None:
    config = HttpClientConfig(cache_dir=tmp_path)

    retry_policy = DefaultHttpPolicyFactory.build_retry_policy(config)
    rate_limiter = DefaultHttpPolicyFactory.build_rate_limiter(config)
    cache = DefaultHttpPolicyFactory.build_response_cache(config)

    assert isinstance(retry_policy, DefaultRetryPolicy)
    assert rate_limiter is not None
    assert cache is not None


def test_default_http_policy_factory_respects_user_overrides(tmp_path) -> None:
    custom_retry = DefaultRetryPolicy(retries=5, backoff_seconds=0.0)
    custom_rate_limiter = _NoopRateLimiter()
    custom_cache = FileCache(cache_dir=tmp_path, ttl_seconds=60)

    config = HttpClientConfig(
        retry_policy=custom_retry,
        rate_limiter=custom_rate_limiter,
        cache=custom_cache,
    )

    retry_policy = DefaultHttpPolicyFactory.build_retry_policy(config)
    rate_limiter = DefaultHttpPolicyFactory.build_rate_limiter(config)
    cache = DefaultHttpPolicyFactory.build_response_cache(config)

    assert retry_policy is custom_retry
    assert rate_limiter is custom_rate_limiter
    assert cache is custom_cache
