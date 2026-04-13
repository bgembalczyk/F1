"""Klasa bazowa dla klientów HTTP."""

import json
from abc import ABC
from abc import abstractmethod
from collections.abc import Callable
from collections.abc import Mapping
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from infrastructure.cache.response_service import ResponseCacheService
from infrastructure.http.config import HttpClientConfig
from infrastructure.http.factories.default_policy import DefaultHttpPolicyFactory
from infrastructure.http.header_resolver import HeaderResolver
from infrastructure.http.protocols.response import HttpResponseProtocol
from infrastructure.http.protocols.session import SessionProtocol
from infrastructure.http.request_executor import RequestExecutor
from infrastructure.http.type_alias import JsonValue


class BaseHttpClient(ABC):
    """Wspólna klasa bazowa dla klientów HTTP."""

    DEFAULT_HEADERS: dict[str, str] = {
        "User-Agent": "F1Scrapers/1.0 contact: bartosz.gembalczyk.stud@pw.edu.pl ",
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(
        self,
        *,
        session: SessionProtocol,
        config: HttpClientConfig,
        request_exception_cls: type[Exception],
    ) -> None:
        """
        Inicjalizacja klienta HTTP.

        Args:
            session: Obiekt sesji (requests.Session lub requests_shim.Session)
            config: Konfiguracja klienta HTTP
            request_exception_cls: Klasa wyjątku dla błędów requestów
        """
        self.session = session
        self.config = config
        self.timeout = int(config.timeout)
        self.request_exception_cls = request_exception_cls

        self.retry_policy = DefaultHttpPolicyFactory.build_retry_policy(config)
        self.rate_limiter = DefaultHttpPolicyFactory.build_rate_limiter(config)
        self.cache = DefaultHttpPolicyFactory.build_response_cache(config)

        merged_headers = dict(self.DEFAULT_HEADERS)
        if config.headers:
            merged_headers.update(config.headers)
        self.default_headers = merged_headers

        self.header_resolver = HeaderResolver(default_headers=self.default_headers)
        self.request_executor = RequestExecutor(
            retry_policy=self.retry_policy,
            rate_limiter=self.rate_limiter,
        )
        self.response_cache_service = ResponseCacheService(cache=self.cache)

    def _request_with_retries(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None,
        timeout: int | None,
        request_func: Callable[..., Any],
    ):
        merged_headers = self.header_resolver.resolve(headers)
        effective_timeout = timeout or self.timeout
        return self.request_executor.execute(
            url=url,
            headers=merged_headers,
            timeout=effective_timeout,
            request_func=request_func,
            request_exception_cls=self.request_exception_cls,
        )

    @abstractmethod
    def get(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        timeout: int | None = None,
    ) -> HttpResponseProtocol:
        """Pobiera URL i zwraca response."""
        ...

    def get_batch(
        self,
        urls: list[str],
        *,
        headers: Mapping[str, str] | None = None,
        timeout: int | None = None,
        max_workers: int = 10,
    ) -> list[HttpResponseProtocol]:
        """Pobiera wiele URLi współbieżnie i zwraca responses."""

        def _get_single(url: str) -> HttpResponseProtocol:
            return self.get(url, headers=headers, timeout=timeout)

        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            return list(pool.map(_get_single, urls))

    def get_text(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        timeout: int | None = None,
    ) -> str:
        """
        Zwraca response.text z obsługą cache.

        Cache działa tylko po URL (headers/timeout są ignorowane w cache key).
        """

        def cache_loader() -> str:
            return self.get(url, headers=headers, timeout=timeout).text

        return self.response_cache_service.get_text(
            url,
            cache_loader,
        )

    def get_json(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        timeout: int | None = None,
    ) -> JsonValue:
        """
        Parsuje JSON z odpowiedzi.

        Bazuje na get_text(), więc cache działa również dla JSON.
        """
        payload = self.get_text(url, headers=headers, timeout=timeout)
        return json.loads(payload)

    def get_text_batch(
        self,
        urls: list[str],
        *,
        headers: Mapping[str, str] | None = None,
        timeout: int | None = None,
        max_workers: int = 10,
    ) -> list[str]:
        """
        Zwraca response.text współbieżnie z obsługą cache.

        Uwaga: implementacja współbieżnie ładuje wiele adresów ułatwiając unikanie problemu N+1.
        """
        def _get_text_single(url: str) -> str:
            return self.get_text(url, headers=headers, timeout=timeout)

        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            return list(pool.map(_get_text_single, urls))

    def get_json_batch(
        self,
        urls: list[str],
        *,
        headers: Mapping[str, str] | None = None,
        timeout: int | None = None,
        max_workers: int = 10,
    ) -> list[JsonValue]:
        """
        Parsuje listę odpowiedzi JSON.
        """
        texts = self.get_text_batch(urls, headers=headers, timeout=timeout, max_workers=max_workers)
        return [json.loads(text) for text in texts]
