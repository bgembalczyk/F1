from contextlib import suppress
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Literal

from infrastructure.http_client.interfaces.http_client_protocol import (
    HttpClientProtocol,
)
from infrastructure.http_client.policies.http import HttpPolicy
from scrapers.base.cache_adapter import CacheBackend
from scrapers.base.export.exporters import DataExporter
from scrapers.base.factory.record_factory import RecordFactory
from scrapers.base.factory.runtime_factory import ScraperRuntimeFactory
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
    record_factory: RecordFactory | None = None
    run_id: str | None = None
    quality_report: bool = False
    error_report: bool = False
    debug_diff_domains: set[str] | None = None
    debug_diff_record_ids: set[str] | None = None
    error_policy: Literal["retry", "skip", "fail-fast"] = "fail-fast"
    error_retry_attempts: int = 1
    # Backward-compatible aliases.
    policy: HttpPolicy | None = None
    transformers: list[RecordTransformer] | None = None
    post_processors: list[RecordPostProcessor] | None = None
    http: HttpOptions = field(default_factory=HttpOptions)
    cache: CacheOptions = field(default_factory=CacheOptions)
    pipeline: PipelineOptions = field(default_factory=PipelineOptions)

    def __post_init__(self) -> None:
        if self.error_policy not in {"retry", "skip", "fail-fast"}:
            msg = "error_policy must be one of: 'retry', 'skip', 'fail-fast'"
            raise ValueError(msg)
        if self.error_retry_attempts < 1:
            msg = "error_retry_attempts must be >= 1"
            raise ValueError(msg)
        if self.policy is not None:
            self.http.policy = self.policy
        else:
            self.policy = self.http.policy
        if self.transformers is not None:
            self.pipeline.transformers = list(self.transformers)
        else:
            self.transformers = self.pipeline.transformers
        if self.post_processors is not None:
            self.pipeline.post_processors = list(self.post_processors)
        else:
            self.post_processors = self.pipeline.post_processors
        if self.source_adapter is not None and not hasattr(
            self.source_adapter,
            "policy",
        ):
            with suppress(AttributeError, TypeError):
                self.source_adapter.policy = self.http.policy

    def __getattribute__(self, name: str):
        value = object.__getattribute__(self, name)
        if name == "source_adapter" and value is not None:
            try:
                policy = object.__getattribute__(self, "http").policy
                value.policy = policy
            except (AttributeError, TypeError):
                pass
        return value

    def to_http_policy(self) -> HttpPolicy:
        return self.http.policy

    def with_fetcher(self) -> HtmlFetcher:
        runtime = ScraperRuntimeFactory().build(
            options=self,
            policy=self.to_http_policy(),
        )
        return runtime.fetcher


@dataclass(slots=True)
class ScraperOptionsBuilder:
    """Fluent builder for composing `ScraperOptions` with nested sub-options."""

    _options: ScraperOptions = field(default_factory=ScraperOptions)

    def with_http(
        self,
        *,
        policy: HttpPolicy | None = None,
        http_client: HttpClientProtocol | None = None,
        timeout: int | None = None,
        retries: int | None = None,
        backoff_seconds: float | None = None,
    ) -> "ScraperOptionsBuilder":
        if policy is not None:
            self._options.http.policy = policy
        if http_client is not None:
            self._options.http.http_client = http_client
        if timeout is not None:
            self._options.http.timeout = timeout
        if retries is not None:
            self._options.http.retries = retries
        if backoff_seconds is not None:
            self._options.http.backoff_seconds = backoff_seconds
        return self

    def with_cache(
        self,
        *,
        cache_dir: Path | str | None = None,
        cache_ttl: int | None = None,
        cache_adapter: CacheBackend | None = None,
    ) -> "ScraperOptionsBuilder":
        if cache_dir is not None:
            self._options.cache.cache_dir = cache_dir
        if cache_ttl is not None:
            self._options.cache.cache_ttl = cache_ttl
        if cache_adapter is not None:
            self._options.cache.cache_adapter = cache_adapter
        return self

    def with_pipeline(
        self,
        *,
        transformers: list[RecordTransformer] | None = None,
        post_processors: list[RecordPostProcessor] | None = None,
    ) -> "ScraperOptionsBuilder":
        if transformers is not None:
            self._options.pipeline.transformers = list(transformers)
        if post_processors is not None:
            self._options.pipeline.post_processors = list(post_processors)
        return self

    def build(self) -> ScraperOptions:
        return self._options
