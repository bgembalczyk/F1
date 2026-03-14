from abc import ABC
from dataclasses import fields
from dataclasses import is_dataclass
from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.ABC import F1Scraper
from scrapers.base.extractors.table import TableExtractor
from scrapers.base.options import ScraperOptions
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.row import TableRow
from scrapers.base.transformers.helpers import apply_transformers
from scrapers.base.transformers.record_factory import RecordFactoryTransformer


class F1TableScraper(F1Scraper, ABC):
    """
    Scraper oparty o pojedynczą tabelę 'wikitable'.

    Konfiguracja przez ScraperConfig:

    - section_id       – id nagłówka sekcji (np. "Constructors_for_the_2025_season"),
                         jeśli None – szukamy po całej stronie.
    - expected_headers – lista nagłówków, które MUSZĄ wystąpić w tabeli (podzbiór).
    - column_map       – mapowanie "nagłówek z tabeli" -> "klucz w dict".
    - columns          – mapowanie klucza/nagłówka -> BaseColumn / spec kolumny
                         (MultiColumn / FuncColumn / TextColumn / IntColumn / ...).
    """

    CONFIG: ScraperConfig | None = None

    # domyślna kolumna dla pól, które nie mają przypisanej logiki
    default_column: BaseColumn = AutoColumn()

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        config: ScraperConfig | None = None,
    ) -> None:
        options = options or ScraperOptions()

        super().__init__(options=options)

        resolved_config = config or self.CONFIG
        if resolved_config is None:
            msg = "ScraperConfig must be provided for F1TableScraper."
            raise ValueError(msg)

        self.config = resolved_config
        self.url = resolved_config.url
        self.section_id = resolved_config.section_id
        self.expected_headers = resolved_config.expected_headers
        self.column_map = resolved_config.column_map
        self.columns = resolved_config.columns
        self.table_css_class = resolved_config.table_css_class
        self.record_factory = resolved_config.record_factory
        self.model_class = resolved_config.model_class
        self.default_column = resolved_config.default_column or AutoColumn()
        self.extractor = TableExtractor(
            config=resolved_config,
            include_urls=self.include_urls,
            normalize_empty_values=options.normalize_empty_values,
            model_fields=self._model_fields(),
            debug_dir=options.debug_dir,
        )
        if self.validator is not None and self.validator.record_factory is None:
            self.validator.set_record_factory(self.record_factory)

    def _parse_soup(self, soup: BeautifulSoup) -> list[Any]:
        """
        Parsuje tabelę przez HtmlTableParser (wybór tabeli + mapowanie nagłówków -> komórki).
        """
        self.extractor.set_run_id(getattr(self, "_run_id", None))
        return self.extractor.extract(soup)

    def parse_row(self, row: TableRow) -> Any | None:
        """
        Dla każdej komórki:
        - ustala nagłówek i klucz,
        - wybiera typ kolumny z `columns`,
        - deleguje całą logikę do handlera kolumny.
        """
        return self.extractor.parse_row(row)

    def _model_fields(self) -> set[str] | None:
        model_class = getattr(self, "model_class", None)
        record_factory = getattr(self, "record_factory", None)
        if model_class is None and isinstance(record_factory, type):
            model_class = record_factory
        if not model_class:
            return None

        # Dla dataclass sprawdzamy czy to typ (klasa), nie instancja
        if isinstance(model_class, type) and is_dataclass(model_class):
            return {f.name for f in fields(model_class)}

        model_fields = getattr(model_class, "model_fields", None)
        if model_fields:
            return set(model_fields)

        pydantic_fields = getattr(model_class, "__fields__", None)
        if pydantic_fields:
            return set(pydantic_fields)

        return None

    def _apply_transformers(self, records: list[Any]) -> list[Any]:
        transformers = list(self.transformers)
        if self.record_factory is not None:
            transformers.append(RecordFactoryTransformer(self.record_factory))
        return apply_transformers(transformers, records, logger=self.logger)
