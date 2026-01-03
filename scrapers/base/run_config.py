from dataclasses import dataclass
from dataclasses import field

from pathlib import Path
from typing import Any

from scrapers.base.options import ScraperOptions


@dataclass(frozen=True)
class RunConfig:
    include_urls: bool = True
    output_dir: str | Path = Path(".")
    debug_dir: str | Path | None = None
    scraper_kwargs: dict[str, Any] = field(default_factory=dict)
    options: ScraperOptions | None = None
