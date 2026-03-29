from typing import Any

from complete_extractor.domain_config import CompleteExtractorDomainConfig
from scrapers.base.composite_scraper import CompositeDataExtractor
from scrapers.base.composite_scraper import CompositeDataExtractorChildren
from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.helpers.wiki import is_wikipedia_redlink
from scrapers.base.options import ScraperOptions
from scrapers.base.source_adapter import IterableSourceAdapter
from scrapers.base.source_adapter import MultiIterableSourceAdapter


class CompleteExtractorBase(CompositeDataExtractor):
    """Wspólny flow dla ekstraktorów typu "lista + szczegóły"."""

    DOMAIN_CONFIG = CompleteExtractorDomainConfig()

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
    ) -> None:
        resolved_options = init_scraper_options(options, include_urls=True)
        super().__init__(options=resolved_options)

    def build_children(self) -> CompositeDataExtractorChildren:
        list_scrapers = self.build_list_scrapers(self.options)
        list_scraper, records_adapter = self._build_list_sources(list_scrapers)

        return CompositeDataExtractorChildren(
            list_scraper=list_scraper,
            single_scraper=self.build_single_scraper(self.options),
            records_adapter=records_adapter,
        )

    def _build_list_sources(
        self,
        list_scrapers: list[Any] | None,
    ) -> tuple[
        Any,
        IterableSourceAdapter[dict[str, Any]]
        | MultiIterableSourceAdapter[dict[str, Any]],
    ]:
        if list_scrapers is None:
            list_scraper = self.build_list_scraper(self.options)
            records_adapter = IterableSourceAdapter(self._records_fetcher(list_scraper))
            return list_scraper, records_adapter
        records_adapter = MultiIterableSourceAdapter(
            [self._records_fetcher(scraper) for scraper in list_scrapers],
        )
        return list_scrapers, records_adapter

    def list_scraper_options(self, options: ScraperOptions) -> ScraperOptions:
        scraper_options = ScraperOptions(
            include_urls=True,
            source_adapter=self.source_adapter,
            debug_dir=options.debug_dir,
        )
        scraper_options.policy = self.http_policy
        return scraper_options

    def single_scraper_options(self, options: ScraperOptions) -> ScraperOptions:
        scraper_options = ScraperOptions(
            source_adapter=self.source_adapter,
            debug_dir=options.debug_dir,
        )
        scraper_options.policy = self.http_policy
        return scraper_options

    def build_list_scraper(self, options: ScraperOptions) -> Any:
        """Zbuduj scraper listy dla przypadków jedno-listowych."""
        scraper_classes = self.DOMAIN_CONFIG.list_scraper_classes
        if len(scraper_classes) > 1:
            msg = (
                f"{self.__class__.__name__} definiuje wiele list scraperów; "
                "użyj build_list_scrapers()."
            )
            raise NotImplementedError(msg)

        scraper_cls = scraper_classes[0] if scraper_classes else None
        if scraper_cls is None:
            msg = (
                f"{self.__class__.__name__} musi ustawić "
                "DOMAIN_CONFIG.list_scraper_classes "
                "lub nadpisać build_list_scraper()."
            )
            raise NotImplementedError(msg)
        return scraper_cls(options=self.list_scraper_options(options))

    def build_list_scrapers(self, options: ScraperOptions) -> list[Any] | None:
        """Opcjonalny hook dla przypadków wielolistowych."""
        scraper_classes = self.DOMAIN_CONFIG.list_scraper_classes
        if len(scraper_classes) <= 1:
            return None
        return [
            scraper_cls(options=self.list_scraper_options(options))
            for scraper_cls in scraper_classes
        ]

    def build_single_scraper(self, options: ScraperOptions) -> Any:
        """Zbuduj scraper szczegółów."""
        scraper_cls = self.DOMAIN_CONFIG.single_scraper_cls
        if scraper_cls is None:
            msg = (
                f"{self.__class__.__name__} musi ustawić "
                "DOMAIN_CONFIG.single_scraper_cls "
                "lub nadpisać build_single_scraper()."
            )
            raise NotImplementedError(msg)
        return scraper_cls(options=self.single_scraper_options(options))

    def extract_detail_url(self, record: dict[str, Any]) -> str | None:
        """Wyciągnij URL szczegółów z rekordu listy na podstawie field path."""
        for field_path in self.DOMAIN_CONFIG.detail_url_field_paths:
            value = self._get_value_by_path(record, field_path)
            if not isinstance(value, str) or not value:
                continue
            if self.DOMAIN_CONFIG.filter_redlinks and is_wikipedia_redlink(value):
                continue
            return value
        return None

    def get_detail_url(self, record: dict[str, Any]) -> str | None:
        return self.extract_detail_url(record)

    def assemble_record(
        self,
        record: dict[str, Any],
        details: dict[str, Any] | None,
    ) -> dict[str, Any]:
        assembler = self.DOMAIN_CONFIG.record_assembler
        if assembler is not None:
            assembled = assembler(record, details)
        else:
            assembled = self.DOMAIN_CONFIG.record_assembly_strategy.assemble(
                record,
                details,
            )

        postprocessor = self.DOMAIN_CONFIG.record_postprocessor
        if postprocessor is not None:
            return postprocessor(assembled)

        return assembled

    @staticmethod
    def _get_value_by_path(source: dict[str, Any], field_path: str) -> Any:
        current: Any = source
        for part in field_path.split("."):
            if not isinstance(current, dict):
                return None
            current = current.get(part)
        return current

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
