from abc import abstractmethod
from typing import Any

from scrapers.base.composite_scraper import CompositeDataExtractor
from scrapers.base.composite_scraper import CompositeDataExtractorChildren
from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.options import ScraperOptions
from scrapers.base.source_adapter import IterableSourceAdapter
from scrapers.base.source_adapter import MultiIterableSourceAdapter


class CompleteExtractorBase(CompositeDataExtractor):
    """Wspólny flow dla ekstraktorów typu "lista + szczegóły"."""

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
    ) -> None:
        resolved_options = init_scraper_options(options, include_urls=True)
        super().__init__(options=resolved_options)

    def build_children(self) -> CompositeDataExtractorChildren:
        list_scrapers = self.build_list_scrapers(self.options)
        list_scraper: Any
        records_adapter: IterableSourceAdapter[dict[str, Any]] | MultiIterableSourceAdapter[
            dict[str, Any]
        ]

        if list_scrapers is None:
            list_scraper = self.build_list_scraper(self.options)
            records_adapter = IterableSourceAdapter(self._records_fetcher(list_scraper))
        else:
            list_scraper = list_scrapers
            records_adapter = MultiIterableSourceAdapter(
                [self._records_fetcher(scraper) for scraper in list_scrapers],
            )

        return CompositeDataExtractorChildren(
            list_scraper=list_scraper,
            single_scraper=self.build_single_scraper(self.options),
            records_adapter=records_adapter,
        )

    def list_scraper_options(self, options: ScraperOptions) -> ScraperOptions:
        return ScraperOptions(
            include_urls=True,
            policy=self.http_policy,
            source_adapter=self.source_adapter,
            debug_dir=options.debug_dir,
        )

    def single_scraper_options(self, options: ScraperOptions) -> ScraperOptions:
        return ScraperOptions(
            policy=self.http_policy,
            source_adapter=self.source_adapter,
            debug_dir=options.debug_dir,
        )

    @abstractmethod
    def build_list_scraper(self, options: ScraperOptions) -> Any:
        """Zbuduj scraper listy dla przypadków jedno-listowych."""

    def build_list_scrapers(self, _options: ScraperOptions) -> list[Any] | None:
        """Opcjonalny hook dla przypadków wielolistowych."""
        return None

    @abstractmethod
    def build_single_scraper(self, options: ScraperOptions) -> Any:
        """Zbuduj scraper szczegółów."""

    @abstractmethod
    def extract_detail_url(self, record: dict[str, Any]) -> str | None:
        """Wyciągnij URL szczegółów z rekordu listy."""

    def get_detail_url(self, record: dict[str, Any]) -> str | None:
        return self.extract_detail_url(record)

    def assemble_record(
        self,
        record: dict[str, Any],
        details: dict[str, Any] | None,
    ) -> dict[str, Any]:
        assembled = dict(record)
        assembled["details"] = details
        return assembled

    def _records_fetcher(self, scraper: Any):
        def _fetch() -> list[dict[str, Any]]:
            try:
                return scraper.fetch()
            except Exception:
                self.logger.exception(
                    "Nie udało się pobrać listy rekordów (%s).",
                    scraper.__class__.__name__,
                )
                return []

        return _fetch
