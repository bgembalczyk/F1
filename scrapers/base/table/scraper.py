from __future__ import annotations

from abc import ABC
from dataclasses import fields, is_dataclass
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from bs4 import BeautifulSoup

from infrastructure.http_client.interfaces import HttpClientProtocol
from infrastructure.http_client.policies import ResponseCache
from scrapers.base.options import ScraperOptions
from scrapers.base.scraper import F1Scraper
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.pipeline import TablePipeline
from scrapers.base.table.row import TableRow

if TYPE_CHECKING:
    import requests
    from scrapers.base.export.exporters import DataExporter


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

    _SKIP = object()

    CONFIG: ScraperConfig | None = None

    # domyślna kolumna dla pól, które nie mają przypisanej logiki
    default_column: BaseColumn = AutoColumn()

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        config: ScraperConfig | None = None,
        include_urls: bool | None = None,
        session: Optional["requests.Session"] = None,
        headers: Optional[Dict[str, str]] = None,
        http_client: Optional["HttpClientProtocol"] = None,
        exporter: Optional["DataExporter"] = None,
        timeout: int | None = None,
        retries: int | None = None,
        cache: "ResponseCache | None" = None,
    ) -> None:
        options = ScraperOptions.resolve(
            options=options,
            include_urls=include_urls,
            session=session,
            headers=headers,
            http_client=http_client,
            exporter=exporter,
            timeout=timeout,
            retries=retries,
            cache=cache,
        )

        super().__init__(options=options)

        resolved_config = config or self.CONFIG
        if resolved_config is None:
            raise ValueError("ScraperConfig must be provided for F1TableScraper.")

        self.config = resolved_config
        self.url = resolved_config.url
        self.section_id = resolved_config.section_id
        self.expected_headers = resolved_config.expected_headers
        self.column_map = resolved_config.column_map
        self.columns = resolved_config.columns
        self.table_css_class = resolved_config.table_css_class
        self.model_class = resolved_config.model_class
        self.default_column = resolved_config.default_column or AutoColumn()
        self.pipeline = TablePipeline(
            config=resolved_config,
            include_urls=self.include_urls,
            skip_sentinel=self._SKIP,
            model_fields=self._model_fields(),
        )

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Parsuje tabelę przez HtmlTableParser (wybór tabeli + mapowanie nagłówków -> komórki).
        """
        return self.pipeline.parse_soup(soup)

    def parse_row(self, row: TableRow) -> Optional[Dict[str, Any]]:
        """
        Dla każdej komórki:
        - ustala nagłówek i klucz,
        - wybiera typ kolumny z `columns`,
        - deleguje całą logikę do handlera kolumny.
        """
        mapped_row = dict(zip(row.headers, row.cells))
        return self.pipeline.parse_row(mapped_row)

    def _model_fields(self) -> set[str] | None:
        model_class = getattr(self, "model_class", None)
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
