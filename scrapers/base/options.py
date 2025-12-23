from __future__ import annotations

from dataclasses import dataclass
import warnings
from typing import Dict, Optional, cast

import requests

from infrastructure.http_client.interfaces import HttpClientProtocol
from infrastructure.http_client.clients import UrllibHttpClient
from infrastructure.http_client.config import HttpClientConfig
from infrastructure.http_client.policies import ResponseCache
from scrapers.base.export.exporters import DataExporter
from scrapers.base.html_fetcher import HtmlFetcher
from scrapers.base.source_adapter import SourceAdapter
from scrapers.base.parsers import SoupParser
from scrapers.config import HttpPolicy, default_http_policy


def build_http_policy(
    *,
    timeout: int = 10,
    retries: int = 0,
    cache: ResponseCache | None = None,
) -> HttpPolicy:
    return HttpPolicy(
        timeout=timeout,
        retries=retries,
        cache=cache,
    )


def init_scraper_options(
    options: "ScraperOptions | None",
    *,
    include_urls: bool | None = None,
) -> "ScraperOptions":
    resolved = options or ScraperOptions()
    if include_urls is not None:
        resolved.include_urls = include_urls
    return resolved


@dataclass(slots=True)
class ScraperOptions:
    """
    Konfiguracja scrapera.

    Legacy pola HTTP (session/headers/timeout/retries/cache) są
    przestarzałe — docelowo używaj HttpPolicy przekazywanego przez `policy`.
    """

    _DEFAULT_TIMEOUT = 10
    _DEFAULT_RETRIES = 0

    include_urls: bool = True
    exporter: Optional[DataExporter] = None
    fetcher: HtmlFetcher | None = None
    source_adapter: SourceAdapter | None = None
    parser: SoupParser | None = None
    policy: HttpPolicy | None = None
    http_client: Optional[HttpClientProtocol] = None
    # Legacy pola HTTP — do usunięcia po migracji na HttpPolicy.
    session: Optional[requests.Session] = None
    headers: Optional[Dict[str, str]] = None
    timeout: int = _DEFAULT_TIMEOUT
    retries: int = _DEFAULT_RETRIES
    cache: ResponseCache | None = None

    def __post_init__(self) -> None:
        if self.timeout <= 0:
            raise ValueError("timeout must be greater than 0")
        if self.retries < 0:
            raise ValueError("retries must be >= 0")
        self._warn_legacy_fields_if_used()

    def _legacy_fields_used(self) -> bool:
        return any(
            (
                self.session is not None,
                self.headers is not None,
                self.cache is not None,
                self.timeout != self._DEFAULT_TIMEOUT,
                self.retries != self._DEFAULT_RETRIES,
            )
        )

    def _warn_legacy_fields_if_used(self) -> None:
        if not self._legacy_fields_used():
            return

        if self.policy is not None:
            message = (
                "Legacy pola HTTP w ScraperOptions są przestarzałe i będą "
                "ignorowane, gdy używasz policy=HttpPolicy."
            )
        else:
            message = (
                "Legacy pola HTTP w ScraperOptions są przestarzałe. "
                "Użyj policy=HttpPolicy."
            )
        warnings.warn(
            message,
            DeprecationWarning,
            stacklevel=3,
        )

    def to_http_policy(self) -> HttpPolicy:
        if self.policy is not None:
            return self.policy
        default_policy = default_http_policy()
        cache = self.cache if self.cache is not None else default_policy.cache
        self.policy = build_http_policy(
            timeout=self.timeout,
            retries=self.retries,
            cache=cache,
        )
        return self.policy

    def _ensure_http_client(self, policy: HttpPolicy) -> HttpClientProtocol:
        if self.http_client is None:
            client_config = HttpClientConfig(
                timeout=policy.timeout,
                retries=policy.retries,
                cache=policy.cache,
                headers=self.headers,
            )
            self.http_client = cast(
                HttpClientProtocol,
                UrllibHttpClient(
                    session=self.session,
                    config=client_config,
                ),
            )
        return self.http_client

    def with_fetcher(self) -> HtmlFetcher:
        if self.fetcher is None:
            if isinstance(self.source_adapter, HtmlFetcher):
                self.fetcher = self.source_adapter
            else:
                policy = self.to_http_policy()
                http_client = self._ensure_http_client(policy)
                self.fetcher = HtmlFetcher(policy=policy, http_client=http_client)
                if self.source_adapter is None:
                    self.source_adapter = self.fetcher
        return self.fetcher

    def with_source_adapter(self) -> SourceAdapter:
        if self.source_adapter is None:
            if self.fetcher is not None:
                self.source_adapter = self.fetcher
            else:
                policy = self.to_http_policy()
                http_client = self._ensure_http_client(policy)
                self.fetcher = HtmlFetcher(policy=policy, http_client=http_client)
                self.source_adapter = self.fetcher
        elif isinstance(self.source_adapter, HtmlFetcher):
            self.fetcher = self.source_adapter
        return self.source_adapter

    @classmethod
    def from_legacy(
        cls,
        *,
        include_urls: bool | None = None,
        exporter: Optional[DataExporter] = None,
        fetcher: HtmlFetcher | None = None,
        parser: SoupParser | None = None,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
        http_client: Optional[HttpClientProtocol] = None,
        timeout: int | None = None,
        retries: int | None = None,
        cache: ResponseCache | None = None,
    ) -> "ScraperOptions | None":
        legacy_values = (
            include_urls,
            exporter,
            fetcher,
            parser,
            session,
            headers,
            http_client,
            timeout,
            retries,
            cache,
        )

        if all(value is None for value in legacy_values):
            return None

        kwargs: dict[str, object] = {}
        if include_urls is not None:
            kwargs["include_urls"] = include_urls
        if exporter is not None:
            kwargs["exporter"] = exporter
        if fetcher is not None:
            kwargs["fetcher"] = fetcher
        if parser is not None:
            kwargs["parser"] = parser
        if session is not None:
            kwargs["session"] = session
        if headers is not None:
            kwargs["headers"] = headers
        if http_client is not None:
            kwargs["http_client"] = http_client
        if timeout is not None:
            kwargs["timeout"] = timeout
        if retries is not None:
            kwargs["retries"] = retries
        if cache is not None:
            kwargs["cache"] = cache

        return cls(**kwargs)

    @classmethod
    def resolve(
        cls,
        *,
        options: "ScraperOptions | None",
        include_urls: bool | None = None,
        session: Optional[requests.Session] = None,
        headers: Optional[Dict[str, str]] = None,
        http_client: Optional[HttpClientProtocol] = None,
        exporter: Optional[DataExporter] = None,
        timeout: int | None = None,
        retries: int | None = None,
        cache: ResponseCache | None = None,
    ) -> "ScraperOptions":
        legacy_used = any(
            value is not None
            for value in (
                include_urls,
                session,
                headers,
                http_client,
                exporter,
                timeout,
                retries,
                cache,
            )
        )

        if options is None:
            resolved = cls.from_legacy(
                include_urls=include_urls,
                session=session,
                headers=headers,
                http_client=http_client,
                exporter=exporter,
                timeout=timeout,
                retries=retries,
                cache=cache,
            )
            if resolved is None:
                return cls()
            warnings.warn(
                "Parametry include_urls/session/headers/http_client/exporter/"
                "timeout/retries/cache w F1TableScraper są przestarzałe. "
                "Przekaż je przez ScraperOptions.",
                DeprecationWarning,
                stacklevel=3,
            )
            return resolved

        if legacy_used:
            warnings.warn(
                "Parametry include_urls/session/headers/http_client/exporter/"
                "timeout/retries/cache w F1TableScraper są ignorowane, gdy "
                "przekazujesz ScraperOptions.",
                DeprecationWarning,
                stacklevel=3,
            )
        return options
