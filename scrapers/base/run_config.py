from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any

from scrapers.base.cache_adapter import CacheBackend
from scrapers.base.options import ScraperOptions


@dataclass(frozen=True)
class RunConfig:
    """Top-level run model for orchestration and scraper construction.

    ``RunConfig`` is the nadrzędny model (source of truth).
    Runtime ``ScraperOptions`` instances should be created via
    ``run_config_to_scraper_options(...)``.

    Notes:
    - Fields duplicated in ``ScraperOptions`` are kept for compatibility with
      existing CLI/API callers.
    - Prefer passing equivalent values through ``options=ScraperOptions(...)``
      for new code paths.
    """

    include_urls: bool = True
    output_dir: str | Path = Path()

    # Deprecated compatibility overrides mirrored in ScraperOptions.
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
