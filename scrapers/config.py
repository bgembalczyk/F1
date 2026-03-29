from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

from scrapers.base.export.exporters import DataExporter
from scrapers.base.helpers.http import default_http_policy
from scrapers.base.html_fetcher import HtmlFetcher
from scrapers.base.options import HttpPolicy
from scrapers.base.parsers.soup import SoupParser


@dataclass(frozen=True)
class ScraperConfig:
    include_urls: bool = True
    exporter: DataExporter | None = None
    fetcher: HtmlFetcher | None = None
    parser: SoupParser | None = None
    policy: HttpPolicy = field(default_factory=default_http_policy)


@dataclass(frozen=True)
class DataPaths:
    base_dir: Path

    @property
    def raw(self) -> Path:
        return self.base_dir / "raw"

    @property
    def normalized(self) -> Path:
        return self.base_dir / "normalized"

    @property
    def checkpoints(self) -> Path:
        return self.base_dir / "checkpoints"

    def legacy_wiki_file(self, category: str, filename: str) -> Path:
        return self.base_dir / "wiki" / category / filename

    def resolve_compatible_input(self, category: str, filename: str) -> Path:
        legacy = self.legacy_wiki_file(category, filename)
        if legacy.exists():
            return legacy
        return self.raw / category / filename


def default_data_paths(*, base_dir: Path | str = Path("data")) -> DataPaths:
    return DataPaths(base_dir=Path(base_dir))


def default_scraper_config() -> ScraperConfig:
    return ScraperConfig()


def default_config() -> ScraperConfig:
    return default_scraper_config()
