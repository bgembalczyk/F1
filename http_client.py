from __future__ import annotations

import importlib
import random
import time
from abc import ABC, abstractmethod
from hashlib import sha256
from pathlib import Path
from typing import Any, Callable, Dict, Optional, cast
from urllib.parse import urlparse

from f1_http import requests_shim
from f1_http.interfaces import HttpClientProtocol

try:  # pragma: no cover - zależne od środowiska
    requests = importlib.import_module("requests")
except Exception:  # pragma: no cover - fallback, gdy brak dependency
    from f1_http import requests_shim as requests  # type: ignore


class RetryPolicy(ABC):
    """Interfejs strategii retry."""

    @property
    @abstractmethod
    def max_retries(self) -> int:
        """Maksymalna liczba ponowień."""

    @abstractmethod
    def should_retry(
        self,
        *,
        response: Any | None,
        exception: Exception | None,
        attempt: int,
    ) -> bool:
        """Czy ponawiać próbę."""

    @abstractmethod
    def backoff_seconds(self, attempt: int) -> float:
        """Ile sekund odczekać przed retry."""


class DefaultRetryPolicy(RetryPolicy):
    """Domyślna strategia retry dla błędów 429/5xx (+częsty 403 od bot-policy)."""

    def __init__(self, *, retries: int = 0, backoff_seconds: float = 0.5) -> None:
        self._max_retries = max(0, int(retries))
        self._backoff_seconds = max(0.0, float(backoff_seconds))

    @property
    def max_retries(self) -> int:
        return self._max_retries

    def should_retry(
        self,
        *,
        response: Any | None,
        exception: Exception | None,
        attempt: int,
    ) -> bool:
        if exception is not None:
            return True
        if response is None:
            return False

        status = int(getattr(response, "status_code", 0) or 0)
        if status == 429 or 500 <= status <= 599:
            return True

        # Wikipedia czasem zwraca 403 z treścią o robot policy / rate limit.
        if status == 403:
            body_text = (getattr(response, "text", "") or "").lower()
            if (
                "too many requests" in body_text
                or "robot policy" in body_text
                or "please respect our robot policy" in body_text
            ):
                return True

        return False

    def backoff_seconds(self, attempt: int) -> float:
        # Exponential backoff + jitter
        base = self._backoff_seconds * (2**attempt)
        return base + random.random()


class RateLimiter(ABC):
    """Interfejs strategii limitowania tempa."""

    @abstractmethod
    def wait(self, url: str) -> None:
        """Wymusza opóźnienie przed wykonaniem requestu."""


class MinDelayRateLimiter(RateLimiter):
    """Minimalny odstęp + jitter między requestami."""

    def __init__(
        self,
        *,
        min_delay_seconds: float = 1.5,
        jitter_seconds: float = 0.7,
        should_limit: Callable[[str], bool] | None = None,
    ) -> None:
        self.min_delay_seconds = max(0.0, float(min_delay_seconds))
        self.jitter_seconds = max(0.0, float(jitter_seconds))
        self.should_limit = should_limit
        self._last_request_ts: float = 0.0

    def wait(self, url: str) -> None:
        if self.should_limit is not None and not self.should_limit(url):
            return
        now = time.monotonic()
        elapsed = now - self._last_request_ts
        delay = self.min_delay_seconds - elapsed
        if delay > 0:
            time.sleep(delay + random.random() * self.jitter_seconds)
        self._last_request_ts = time.monotonic()


class ResponseCache(ABC):
    """Interfejs cache dla odpowiedzi."""

    @abstractmethod
    def get(self, url: str) -> Optional[str]:
        """Zwraca tekst z cache lub None."""

    @abstractmethod
    def set(self, url: str, text: str) -> None:
        """Zapisuje tekst do cache."""


class FileCache(ResponseCache):
    """Cache oparty o pliki z TTL."""

    def __init__(self, *, cache_dir: Path | str, ttl_seconds: int = 0) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = max(0, int(ttl_seconds))

    def get(self, url: str) -> Optional[str]:
        path = self._cache_path_for_url(url)
        if not self._is_cache_fresh(path):
            return None
        return path.read_text(encoding="utf-8")

    def set(self, url: str, text: str) -> None:
        path = self._cache_path_for_url(url)
        path.write_text(text, encoding="utf-8")

    def _cache_path_for_url(self, url: str) -> Path:
        digest = sha256(url.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{digest}.html"

    def _is_cache_fresh(self, path: Path) -> bool:
        # ttl_seconds == 0 => cache wyłączony
        if not path.exists() or self.ttl_seconds <= 0:
            return False
        age_seconds = time.time() - path.stat().st_mtime
        return age_seconds <= self.ttl_seconds


class WikipediaCachePolicy(ResponseCache):
    """Cache tylko dla Wikipedia."""

    def __init__(self, cache: ResponseCache) -> None:
        self.cache = cache

    def get(self, url: str) -> Optional[str]:
        if not self._is_wikipedia_url(url):
            return None
        return self.cache.get(url)

    def set(self, url: str, text: str) -> None:
        if not self._is_wikipedia_url(url):
            return
        self.cache.set(url, text)

    @staticmethod
    def _is_wikipedia_url(url: str) -> bool:
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower()
        return hostname == "wikipedia.org" or hostname.endswith(".wikipedia.org")


class BaseHttpClient(ABC, HttpClientProtocol):
    """Wspólna klasa bazowa dla klientów HTTP."""

    DEFAULT_HEADERS: Dict[str, str] = {
        "User-Agent": "F1Scrapers/1.0 contact: bartosz.gembalczyk.stud@pw.edu.pl ",
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(
        self,
        *,
        session: Any,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 10,
        retry_policy: RetryPolicy | None = None,
        rate_limiter: RateLimiter | None = None,
        request_exception_cls: type[Exception],
    ) -> None:
        self.session = session
        self.timeout = int(timeout)

        self.retry_policy = retry_policy or DefaultRetryPolicy(
            retries=0, backoff_seconds=0.5
        )
        self.rate_limiter = rate_limiter or MinDelayRateLimiter()

        self.request_exception_cls = request_exception_cls

        merged_headers = dict(self.DEFAULT_HEADERS)
        if headers:
            merged_headers.update(headers)

        # session.headers może nie istnieć w shimach — zabezpieczenie
        session_headers = getattr(self.session, "headers", None)
        if session_headers is not None and hasattr(session_headers, "update"):
            session_headers.update(merged_headers)

    def _backoff_sleep(self, attempt: int) -> None:
        delay = self.retry_policy.backoff_seconds(attempt)
        if delay > 0:
            time.sleep(delay)

    def _request_with_retries(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]],
        timeout: Optional[int],
        request_func: Callable[..., Any],
    ):
        attempts = self.retry_policy.max_retries + 1

        for attempt in range(attempts):
            if self.rate_limiter is not None:
                self.rate_limiter.wait(url)

            try:
                response = request_func(
                    url,
                    headers=headers,
                    timeout=timeout or self.timeout,
                )
            except self.request_exception_cls as exc:
                if (
                    attempt >= self.retry_policy.max_retries
                    or not self.retry_policy.should_retry(
                        response=None,
                        exception=exc,
                        attempt=attempt,
                    )
                ):
                    raise
                self._backoff_sleep(attempt)
                continue

            if self.retry_policy.should_retry(
                response=response,
                exception=None,
                attempt=attempt,
            ):
                if attempt >= self.retry_policy.max_retries:
                    response.raise_for_status()
                self._backoff_sleep(attempt)
                continue

            response.raise_for_status()
            return cast(Any, response)

        assert False, "Unreachable code"

    @abstractmethod
    def get(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ):
        """Pobiera URL i zwraca response."""
        ...

    def get_text(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> str:
        response = self.get(url, headers=headers, timeout=timeout)
        return response.text


class HttpClient(BaseHttpClient):
    """Klient HTTP (requests) ze współdzieloną sesją, retry, rate-limit i cache."""

    def __init__(
        self,
        *,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 10,
        retries: int = 0,
        backoff_seconds: float = 0.5,
        min_delay_seconds: float = 1.5,
        jitter_seconds: float = 0.7,
        retry_policy: RetryPolicy | None = None,
        rate_limiter: RateLimiter | None = None,
        cache: ResponseCache | None = None,
        cache_dir: Path | str | None = None,
        cache_ttl_days: int = 30,
    ) -> None:
        session = session or requests.Session()

        if retry_policy is None:
            retry_policy = DefaultRetryPolicy(
                retries=retries, backoff_seconds=backoff_seconds
            )

        if rate_limiter is None:
            rate_limiter = MinDelayRateLimiter(
                min_delay_seconds=min_delay_seconds,
                jitter_seconds=jitter_seconds,
            )

        super().__init__(
            session=session,
            headers=headers,
            timeout=timeout,
            retry_policy=retry_policy,
            rate_limiter=rate_limiter,
            request_exception_cls=requests.RequestException,
        )

        if cache is None:
            if cache_dir is None:
                cache_dir = Path(__file__).parent / "data" / "wiki_cache"
            cache_ttl_seconds = max(0, int(cache_ttl_days)) * 24 * 60 * 60
            cache = WikipediaCachePolicy(
                FileCache(cache_dir=cache_dir, ttl_seconds=cache_ttl_seconds)
            )
        self.cache = cache

    def get(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ):
        return self._request_with_retries(
            url,
            headers=headers,
            timeout=timeout,
            request_func=self.session.get,
        )

    def get_text(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> str:
        if self.cache is not None:
            cached = self.cache.get(url)
            if cached is not None:
                return cached

        response = self.get(url, headers=headers, timeout=timeout)
        text = response.text

        if self.cache is not None:
            self.cache.set(url, text)

        return text


class UrllibHttpClient(BaseHttpClient):
    """Klient HTTP oparty o urllib (requests_shim), zgodny z HttpClientProtocol."""

    def __init__(
        self,
        *,
        session: Optional[requests_shim.Session] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 10,
        retries: int = 0,
        backoff_seconds: float = 0.5,
        min_delay_seconds: float = 1.5,
        jitter_seconds: float = 0.7,
        retry_policy: RetryPolicy | None = None,
        rate_limiter: RateLimiter | None = None,
        cache: ResponseCache | None = None,
        cache_dir: Path | str | None = None,
        cache_ttl_days: int = 30,
    ) -> None:
        session = session or requests_shim.Session()

        if retry_policy is None:
            retry_policy = DefaultRetryPolicy(
                retries=retries, backoff_seconds=backoff_seconds
            )

        if rate_limiter is None:
            rate_limiter = MinDelayRateLimiter(
                min_delay_seconds=min_delay_seconds,
                jitter_seconds=jitter_seconds,
            )

        super().__init__(
            session=session,
            headers=headers,
            timeout=timeout,
            retry_policy=retry_policy,
            rate_limiter=rate_limiter,
            request_exception_cls=requests_shim.RequestException,
        )

        if cache is None:
            if cache_dir is None:
                cache_dir = Path(__file__).parent / "data" / "wiki_cache"
            cache_ttl_seconds = max(0, int(cache_ttl_days)) * 24 * 60 * 60
            cache = WikipediaCachePolicy(
                FileCache(cache_dir=cache_dir, ttl_seconds=cache_ttl_seconds)
            )
        self.cache = cache

    def get(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ):
        return self._request_with_retries(
            url,
            headers=headers,
            timeout=timeout,
            request_func=self.session.get,
        )

    def get_text(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> str:
        if self.cache is not None:
            cached = self.cache.get(url)
            if cached is not None:
                return cached

        response = self.get(url, headers=headers, timeout=timeout)
        text = response.text

        if self.cache is not None:
            self.cache.set(url, text)

        return text
