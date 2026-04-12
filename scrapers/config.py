import warnings
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

from exporters.data import DataExporter
from infrastructure.helpers import default_http_policy
from infrastructure.http.policies.http import HttpPolicy
from scrapers.html_fetcher import HtmlFetcher
from scrapers.parsers.soup import SoupParser


@dataclass(frozen=True)
class RuntimeConfig:
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

    def legacy_wiki_file(self, category: str, filename: str) -> Path:
        return self.base_dir / category / filename

    def resolve_compatible_input(self, category: str, filename: str) -> Path:
        legacy = self.legacy_wiki_file(category, filename)
        if legacy.exists():
            return legacy
        return self.raw / category / filename




def __getattr__(name: str) -> object:
    if name == "ScraperConfig":
        warnings.warn(
            "scrapers.config.ScraperConfig is deprecated; use RuntimeConfig.",
            DeprecationWarning,
            stacklevel=2,
        )
        return RuntimeConfig
    raise AttributeError(name)
