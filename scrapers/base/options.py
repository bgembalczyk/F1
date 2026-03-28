from collections.abc import Callable
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from infrastructure.http_client.interfaces.http_client_protocol import (
    HttpClientProtocol,
)
from infrastructure.http_client.policies.http import HttpPolicy
from scrapers.base.cache_adapter import CacheBackend
from scrapers.base.export.exporters import DataExporter
from scrapers.base.helpers.http import default_http_policy
from scrapers.base.html_fetcher import HtmlFetcher
from scrapers.base.parsers.soup import SoupParser
from scrapers.base.post_processors import RecordPostProcessor
from scrapers.base.source_adapter import SourceAdapter
from scrapers.base.transformers.record_transformer import RecordTransformer
from validation.validator_base import RecordValidator


@dataclass(slots=True)
class HttpOptions:
    policy: HttpPolicy = field(default_factory=default_http_policy)
    http_client: HttpClientProtocol | None = None
    timeout: int | None = None
    retries: int | None = None
    backoff_seconds: float | None = None


@dataclass(slots=True)
class CacheOptions:
    cache_dir: Path | str | None = None
    cache_ttl: int | None = None
    cache_adapter: CacheBackend | None = None


@dataclass(slots=True)
class PipelineOptions:
    transformers: list[RecordTransformer] = field(default_factory=list)
    post_processors: list[RecordPostProcessor] = field(default_factory=list)


@dataclass(slots=True)
class ScraperOptions:
    """Lekki kontener danych wejściowych konfiguracji scrapera."""

    include_urls: bool = True
    exporter: DataExporter | None = None
    fetcher: HtmlFetcher | None = None
    source_adapter: SourceAdapter | None = None
    parser: SoupParser | None = None
    validator: RecordValidator | None = None
    validation_mode: str = "soft"
    debug_dir: Path | None = None
    normalize_empty_values: bool = True
    record_factory: Callable[[Mapping[str, Any]], Any] | type | None = None
    run_id: str | None = None
    quality_report: bool = False
    error_report: bool = False
    http: HttpOptions = field(default_factory=HttpOptions)
    cache: CacheOptions = field(default_factory=CacheOptions)
    pipeline: PipelineOptions = field(default_factory=PipelineOptions)

    @property
    def policy(self) -> HttpPolicy:
        return self.http.policy

    @policy.setter
    def policy(self, value: HttpPolicy) -> None:
        self.http.policy = value

    @property
    def http_client(self) -> HttpClientProtocol | None:
        return self.http.http_client

    @http_client.setter
    def http_client(self, value: HttpClientProtocol | None) -> None:
        self.http.http_client = value

    @property
    def http_timeout(self) -> int | None:
        return self.http.timeout

    @http_timeout.setter
    def http_timeout(self, value: int | None) -> None:
        self.http.timeout = value

    @property
    def http_retries(self) -> int | None:
        return self.http.retries

    @http_retries.setter
    def http_retries(self, value: int | None) -> None:
        self.http.retries = value

    @property
    def http_backoff_seconds(self) -> float | None:
        return self.http.backoff_seconds

    @http_backoff_seconds.setter
    def http_backoff_seconds(self, value: float | None) -> None:
        self.http.backoff_seconds = value

    @property
    def cache_dir(self) -> Path | str | None:
        return self.cache.cache_dir

    @cache_dir.setter
    def cache_dir(self, value: Path | str | None) -> None:
        self.cache.cache_dir = value

    @property
    def cache_ttl(self) -> int | None:
        return self.cache.cache_ttl

    @cache_ttl.setter
    def cache_ttl(self, value: int | None) -> None:
        self.cache.cache_ttl = value

    @property
    def cache_adapter(self) -> CacheBackend | None:
        return self.cache.cache_adapter

    @cache_adapter.setter
    def cache_adapter(self, value: CacheBackend | None) -> None:
        self.cache.cache_adapter = value

    @property
    def transformers(self) -> list[RecordTransformer]:
        return self.pipeline.transformers

    @transformers.setter
    def transformers(self, value: list[RecordTransformer] | None) -> None:
        self.pipeline.transformers = list(value or [])

    @property
    def post_processors(self) -> list[RecordPostProcessor]:
        return self.pipeline.post_processors

    @post_processors.setter
    def post_processors(self, value: list[RecordPostProcessor] | None) -> None:
        self.pipeline.post_processors = list(value or [])
