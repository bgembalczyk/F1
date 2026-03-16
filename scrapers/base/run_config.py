from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any

from scrapers.base.cache_adapter import CacheBackend
from scrapers.base.options import ScraperOptions


@dataclass(frozen=True)
class RunConfig:
    include_urls: bool = True
    output_dir: str | Path = Path()
    output_category: str | None = None
    output_layer: str | None = None
    legacy_output_enabled: bool = False
    parser_version: str | None = None
    schema_version: str | None = None
    debug_dir: str | Path | None = None
    cache_dir: str | Path | None = None
    cache_ttl: int | None = None
    cache_adapter: CacheBackend | None = None
    http_timeout: int | None = None
    http_retries: int | None = None
    http_backoff_seconds: float | None = None
    quality_report: bool = False
    error_report: bool = False
    scraper_kwargs: dict[str, Any] = field(default_factory=dict)
    options: ScraperOptions | None = None
