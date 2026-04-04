"""Klasa bazowa dla klientów HTTP."""

import json
from abc import ABC
from abc import abstractmethod
from collections.abc import Callable
from collections.abc import Mapping
from typing import Any

from infrastructure.http_client.components.header_resolver import HeaderResolver
from infrastructure.http_client.components.request_executor import RequestExecutor
from infrastructure.http_client.components.response_cache_service import (
    ResponseCacheService,
)
from infrastructure.http_client.config import HttpClientConfig
from infrastructure.http_client.factories.default_http_policy_factory import (
    DefaultHttpPolicyFactory,
)
from infrastructure.http_client.interfaces.http_client_protocol import JsonValue
from infrastructure.http_client.interfaces.http_response_protocol import (
    HttpResponseProtocol,
)
from infrastructure.http_client.interfaces.session_protocol import SessionProtocol


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
        cache_loader = lambda: self.get(url, headers=headers, timeout=timeout).text
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
