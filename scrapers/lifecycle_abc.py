from abc import ABC
from abc import abstractmethod

from bs4 import BeautifulSoup

from scrapers.results import ScrapeResult
from scrapers.runners.pipeline_runner import RawRecord
from validation.validator_base import ExportRecord


class ScraperLifecycleABC(ABC):
    @abstractmethod
    def fetch(self) -> list[ExportRecord]:
        """Execute fetch lifecycle and return exportable records."""

    @abstractmethod
    def parse(self, soup: BeautifulSoup) -> list[RawRecord]:
        """Parse BeautifulSoup document into raw records."""

    @abstractmethod
    def build_result(self, data: list[ExportRecord] | None = None) -> ScrapeResult:
        """Build finalized scrape result with metadata."""

