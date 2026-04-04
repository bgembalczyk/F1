from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

from scrapers.base.export.exporters import DataExporter
from scrapers.base.html_fetcher import HtmlFetcher
from scrapers.base.options import HttpPolicy
from scrapers.base.options import default_http_policy
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
    base_dir: Path = Path("../../data")

    @property
    def raw(self) -> Path:
        return self.base_dir / "raw"

    @property
    def normalized(self) -> Path:
        return self.base_dir / "normalized"

    @property
    def checkpoints(self) -> Path:
        return self.base_dir / "checkpoints"

    def raw_input_file(self, category: str, filename: str) -> Path:
        return self.raw / category / filename


def default_data_paths(*, base_dir: Path = Path("../../data")) -> DataPaths:
    return DataPaths(base_dir=base_dir)
