from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from scrapers.base.composite_scraper import CompositeDataExtractor
from scrapers.base.composite_scraper import CompositeDataExtractorChildren
from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.options import ScraperOptions
from scrapers.base.source_adapter import IterableSourceAdapter
from scrapers.base.source_adapter import MultiIterableSourceAdapter


@dataclass(frozen=True)
class CompleteExtractorDomainConfig:
    """Konfiguracja domeny dla CompleteExtractorBase.

    Jak dodać nową domenę bez kopiowania klasy:
    1) ustaw `list_scraper_cls` i `single_scraper_cls`,
    2) ustaw `detail_url_field_path` (np. ``"driver.url"``),
    3) opcjonalnie dopasuj `assemble_record_strategy` i parametry,
    4) opcjonalnie dodaj `record_postprocessor`, gdy wynik wymaga finalnej normalizacji.

    Dzięki temu nowy extractor często ogranicza się do kilku atrybutów klasowych.
    """

    list_scraper_cls: type[Any] | None = None
    single_scraper_cls: type[Any] | None = None
    detail_url_field_path: str | None = None
    assemble_record_strategy: str = "attach_details"
    assemble_record_params: dict[str, Any] | None = None
    record_postprocessor: Callable[[dict[str, Any]], dict[str, Any]] | None = None


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
        list_scraper: Any
        records_adapter: (
            IterableSourceAdapter[dict[str, Any]]
            | MultiIterableSourceAdapter[dict[str, Any]]
        )

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

    def build_list_scraper(self, options: ScraperOptions) -> Any:
        """Zbuduj scraper listy dla przypadków jedno-listowych."""
        scraper_cls = self.DOMAIN_CONFIG.list_scraper_cls
        if scraper_cls is None:
            msg = (
                f"{self.__class__.__name__} musi ustawić "
                "DOMAIN_CONFIG.list_scraper_cls "
                "lub nadpisać build_list_scraper()."
            )
            raise NotImplementedError(msg)
        return scraper_cls(options=self.list_scraper_options(options))

    def build_list_scrapers(self, _options: ScraperOptions) -> list[Any] | None:
        """Opcjonalny hook dla przypadków wielolistowych."""
        return None

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
        field_path = self.DOMAIN_CONFIG.detail_url_field_path
        if not field_path:
            return None

        value = self._get_value_by_path(record, field_path)
        if isinstance(value, str) and value:
            return value
        return None

    def get_detail_url(self, record: dict[str, Any]) -> str | None:
        return self.extract_detail_url(record)

    def assemble_record(
        self,
        record: dict[str, Any],
        details: dict[str, Any] | None,
    ) -> dict[str, Any]:
        assembled = self._assemble_record_by_strategy(record, details)

        postprocessor = self.DOMAIN_CONFIG.record_postprocessor
        if postprocessor is not None:
            return postprocessor(assembled)

        return assembled

    def _assemble_record_by_strategy(
        self,
        record: dict[str, Any],
        details: dict[str, Any] | None,
    ) -> dict[str, Any]:
        strategy = self.DOMAIN_CONFIG.assemble_record_strategy
        params = self.DOMAIN_CONFIG.assemble_record_params or {}

        if strategy == "attach_details":
            details_key = params.get("details_key", "details")
            assembled = dict(record)
            assembled[details_key] = details
            return assembled

        if strategy == "extract_detail_field":
            detail_field = params["detail_field"]
            target_key = params.get("target_key", detail_field)
            assembled = dict(record)
            assembled[target_key] = (
                details.get(detail_field) if isinstance(details, dict) else None
            )
            return assembled

        if strategy == "bundle":
            record_field = params["record_field"]
            details_key = params.get("details_key", "details")
            record_value = record.get(record_field)
            details_default = params.get("details_default", {})
            return {
                record_field: record_value if isinstance(record_value, dict) else {},
                details_key: details if details is not None else details_default,
            }

        msg = f"Nieznana strategia składania rekordu: {strategy}"
        raise ValueError(msg)

    def _get_value_by_path(self, source: dict[str, Any], field_path: str) -> Any:
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
