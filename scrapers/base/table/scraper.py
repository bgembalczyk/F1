from __future__ import annotations

from abc import ABC
from dataclasses import asdict, fields, is_dataclass
from typing import Optional, Sequence, Mapping, List, Dict, Any, TYPE_CHECKING

from bs4 import BeautifulSoup, Tag

from scrapers.base.helpers.utils import clean_wiki_text, extract_links_from_cell
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.helpers.wiki import extract_links_from_cell, find_section_elements
from scrapers.base.scraper import F1Scraper
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.base.table.config import ScraperConfig

if TYPE_CHECKING:
    import requests

    from http_client.interfaces import HttpClientProtocol
    from http_client.policies import ResponseCache
    from scrapers.base.exporters import DataExporter
from scrapers.base.table.columns.registry import resolve_column_type
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.base.table.parser import HtmlTableParser


class F1TableScraper(F1Scraper, ABC):
    """
    Scraper oparty o pojedynczą tabelę 'wikitable'.

    Konfiguracja przez ScraperConfig:

    - section_id    – id nagłówka sekcji (np. "Constructors_for_the_2025_season"),
                       jeśli None – szukamy po całej stronie.
    - expected_headers – lista nagłówków, które MUSZĄ wystąpić w tabeli (podzbiór).
    - column_map    – mapowanie "nagłówek z tabeli" -> "klucz w dict".
    - columns       – mapowanie klucza/nagłówka -> BaseColumn
                      (MultiColumn / FuncColumn / TextColumn / IntColumn / ...).
    """

    _SKIP = object()

    CONFIG: ScraperConfig | None = None

    _REF_RE = re.compile(r"\[\s*[^]]+\s*]")
    # domyślna kolumna dla pól, które nie mają przypisanej logiki
    default_column: BaseColumn = AutoColumn()

    # --- szablon parsowania ---
    def __init__(
        self,
        *,
        config: ScraperConfig | None = None,
        include_urls: bool = True,
        session: Optional["requests.Session"] = None,
        headers: Optional[Dict[str, str]] = None,
        http_client: Optional["HttpClientProtocol"] = None,
        exporter: Optional["DataExporter"] = None,
        timeout: int = 10,
        retries: int = 0,
        cache: "ResponseCache | None" = None,
    ) -> None:
        super().__init__(
            include_urls=include_urls,
            session=session,
            headers=headers,
            http_client=http_client,
            exporter=exporter,
            timeout=timeout,
            retries=retries,
            cache=cache,
        )
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
        self.default_column = resolved_config.default_column

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        parser = HtmlTableParser(
            section_id=self.section_id,
            expected_headers=self.expected_headers,
            table_css_class=self.table_css_class,
        )
        for row in parser.parse(soup):
            record = self.parse_row(row)
            if record:
                records.append(record)

        return records

    # --- hook per-wiersz ---

    def parse_row(
        self,
        row: Mapping[str, Tag],
    ) -> Optional[Dict[str, Any]]:
        """
        Dla każdej komórki:
        - ustala nagłówek i klucz,
        - wybiera typ kolumny z column_types,
        - deleguje całą logikę do handlera kolumny.
        """
        record: Dict[str, Any] = {}
        model_fields = self._model_fields()

        for header, cell in row.items():
            key = self.column_map.get(header, self._normalize_header(header))

            raw_text = cell.get_text(" ", strip=True)
            clean_text = clean_wiki_text(raw_text)

            links: list[dict[str, Any]] = []
            if self.include_urls:
                links = extract_links_from_cell(cell, full_url=self._full_url)

            ctx = ColumnContext(
                header=header,
                key=key,
                raw_text=raw_text,
                clean_text=clean_text,
                links=links,
                cell=cell,
                skip_sentinel=self._SKIP,
                model_fields=model_fields,
            )

            col_spec = (
                self.columns.get(key) or self.columns.get(header) or self.default_column
            )
            col = resolve_column_type(col_spec)

            col.apply(ctx, record)

        if self.model_class:
            model = self.model_class(**record)
            if hasattr(model, "model_dump"):
                return model.model_dump()
            if hasattr(model, "dict"):
                return model.dict()
            if is_dataclass(model):
                return asdict(model)

        return record

    @staticmethod
    def _normalize_header(header: str) -> str:
        return (
            header.strip()
            .lower()
            .replace(" ", "_")
            .replace("(", "")
            .replace(")", "")
            .replace("/", "_")
        )

    def _model_fields(self) -> set[str] | None:
        model_class = getattr(self, "model_class", None)
        if not model_class:
            return None

        if is_dataclass(model_class):
            return {f.name for f in fields(model_class)}

        model_fields = getattr(model_class, "model_fields", None)
        if model_fields:
            return set(model_fields)

        pydantic_fields = getattr(model_class, "__fields__", None)
        if pydantic_fields:
            return set(pydantic_fields)

        return None
