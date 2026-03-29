from typing import Any

from complete_extractor.domain_config import CompleteExtractorDomainConfig
from scrapers.base.composite_scraper import CompositeDataExtractor
from scrapers.base.composite_scraper import CompositeDataExtractorChildren
from scrapers.base.composite_scraper import ListScraperProtocol
from scrapers.base.composite_scraper import SingleScraperProtocol
from scrapers.base.composite_dto import CompositeRecordDTO
from scrapers.base.composite_dto import DetailRecordDTO
from scrapers.base.composite_dto import ListRecordDTO
from scrapers.base.errors import DomainParseError
from scrapers.base.errors import ScraperNetworkError
from scrapers.base.errors import ScraperParseError
from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.helpers.wiki import is_wikipedia_redlink
from scrapers.base.options import ScraperOptions
from scrapers.base.source_adapter import IterableSourceAdapter
from scrapers.base.source_adapter import MultiIterableSourceAdapter
from infrastructure.http_client.requests_shim.request_error import RequestError


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
        list_scrapers: list[ListScraperProtocol] | None,
    ) -> tuple[
        ListScraperProtocol | list[ListScraperProtocol],
        IterableSourceAdapter[ListRecordDTO]
        | MultiIterableSourceAdapter[ListRecordDTO],
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
        scraper_options.http.policy = self.http_policy
        return scraper_options

    def single_scraper_options(self, options: ScraperOptions) -> ScraperOptions:
        scraper_options = ScraperOptions(
            source_adapter=self.source_adapter,
            debug_dir=options.debug_dir,
        )
        scraper_options.http.policy = self.http_policy
        return scraper_options

    def build_list_scraper(self, options: ScraperOptions) -> ListScraperProtocol:
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

    def build_list_scrapers(
        self,
        options: ScraperOptions,
    ) -> list[ListScraperProtocol] | None:
        """Opcjonalny hook dla przypadków wielolistowych."""
        scraper_classes = self.DOMAIN_CONFIG.list_scraper_classes
        if len(scraper_classes) <= 1:
            return None
        return [
            scraper_cls(options=self.list_scraper_options(options))
            for scraper_cls in scraper_classes
        ]

    def build_single_scraper(self, options: ScraperOptions) -> SingleScraperProtocol:
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

    def extract_detail_url(self, record: ListRecordDTO) -> str | None:
        """Wyciągnij URL szczegółów z rekordu listy na podstawie field path."""
        payload = record.to_dict()
        for field_path in self.DOMAIN_CONFIG.detail_url_field_paths:
            value = self._get_value_by_path(payload, field_path)
            if not isinstance(value, str) or not value:
                continue
            if self.DOMAIN_CONFIG.filter_redlinks and is_wikipedia_redlink(value):
                continue
            return value
        return None

    def get_detail_url(self, record: ListRecordDTO) -> str | None:
        return self.extract_detail_url(record)

    def assemble_record(
        self,
        record: ListRecordDTO,
        details: DetailRecordDTO | None,
    ) -> CompositeRecordDTO:
        record_payload = record.to_dict()
        details_payload = details.to_dict() if details is not None else None
        assembler = self.DOMAIN_CONFIG.record_assembler
        if assembler is not None:
            assembled = assembler(record_payload, details_payload)
        else:
            assembled = self.DOMAIN_CONFIG.record_assembly_strategy.assemble(
                record_payload,
                details_payload,
            )

        postprocessor = self.DOMAIN_CONFIG.record_postprocessor
        if postprocessor is not None:
            return CompositeRecordDTO.from_dict(postprocessor(assembled))

        return CompositeRecordDTO.from_dict(assembled)

    @staticmethod
    def _get_value_by_path(source: dict[str, Any], field_path: str) -> Any:
        current: Any = source
        for part in field_path.split("."):
            if not isinstance(current, dict):
                return None
            current = current.get(part)
        return current

    def _records_fetcher(self, scraper: ListScraperProtocol):
        def _fetch() -> list[ListRecordDTO]:
            try:
                records = scraper.fetch()
                return [self.json_boundary.list_from_json(record) for record in records]
            except (
                RequestError,
                ScraperNetworkError,
                ScraperParseError,
                DomainParseError,
            ):
                self.logger.exception(
                    "Nie udało się pobrać listy rekordów (%s).",
                    scraper.__class__.__name__,
                )
                return []

        return _fetch
