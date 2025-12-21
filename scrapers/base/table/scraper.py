from __future__ import annotations

import re
from abc import ABC
from dataclasses import fields, is_dataclass
import warnings
from typing import Any, Dict, List, Mapping, Optional, TYPE_CHECKING

from bs4 import BeautifulSoup, Tag

from infrastructure.http_client.interfaces import HttpClientProtocol
from scrapers.base.helpers.wiki import clean_wiki_text
from scrapers.base.helpers.wiki import extract_links_from_cell
from scrapers.base.options import ScraperOptions
from scrapers.base.scraper import F1Scraper
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.parser import HtmlTableParser

if TYPE_CHECKING:
    import requests
    from infrastructure.http_client.policies import ResponseCache
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

    _REF_RE = re.compile(r"\[\s*[^]]+\s*]")

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
        legacy_used = any(
            value is not None
            for value in (
                include_urls,
                session,
                headers,
                http_client,
                exporter,
                timeout,
                retries,
                cache,
            )
        )

        if options is None:
            options = ScraperOptions.from_legacy(
                include_urls=include_urls,
                session=session,
                headers=headers,
                http_client=http_client,
                exporter=exporter,
                timeout=timeout,
                retries=retries,
                cache=cache,
            )
            if options is None:
                options = ScraperOptions()
            else:
                warnings.warn(
                    "Parametry include_urls/session/headers/http_client/exporter/"
                    "timeout/retries/cache w F1TableScraper są przestarzałe. "
                    "Przekaż je przez ScraperOptions.",
                    DeprecationWarning,
                    stacklevel=2,
                )
        elif legacy_used:
            warnings.warn(
                "Parametry include_urls/session/headers/http_client/exporter/"
                "timeout/retries/cache w F1TableScraper są ignorowane, gdy "
                "przekazujesz ScraperOptions.",
                DeprecationWarning,
                stacklevel=2,
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

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Parsuje tabelę przez HtmlTableParser (wybór tabeli + mapowanie nagłówków -> komórki).

        Pomijamy wiersze będące kopią nagłówka (częste w <tfoot> albo jako
        "repeated header" w środku tabeli).
        """
        records: List[Dict[str, Any]] = []

        parser = HtmlTableParser(
            section_id=self.section_id,
            expected_headers=self.expected_headers,
            table_css_class=self.table_css_class,
        )

        for row in parser.parse(soup):
            if self._is_repeated_header_row(row):
                continue

            record = self.parse_row(row)
            if record:
                records.append(record)

        return records

    def _is_repeated_header_row(self, row: Mapping[str, Any]) -> bool:
        """
        Wykrywa "footer / repeated header row":

        - jeśli parser przemyca źródłowy <tr> w metadanych (__row__/__tr__/etc.),
          porównujemy teksty komórek w tym <tr> do listy nagłówków (kluczy row)
          w tej samej kolejności;
        - jeżeli nie ma <tr>, robimy bezpieczny fallback: nic nie pomijamy.
        """
        tr = None
        if hasattr(row, "get"):
            tr = row.get("__row__") or row.get("_row") or row.get("__tr__")

        if not isinstance(tr, Tag):
            return False

        # Nagłówki w kolejności tabeli: tylko str-key'e i bez metadanych.
        headers_ordered: List[str] = [
            h
            for h in row.keys()
            if isinstance(h, str) and h not in {"__row__", "_row", "__tr__"}
        ]
        if not headers_ordered:
            return False

        headers_clean = [clean_wiki_text(h) for h in headers_ordered]

        cells = tr.find_all(["th", "td"], recursive=False)
        if not cells:
            return False

        cell_texts = [clean_wiki_text(c.get_text(" ", strip=True)) for c in cells]

        return len(cell_texts) == len(headers_clean) and cell_texts == headers_clean

    def parse_row(self, row: Mapping[str, Tag]) -> Optional[Dict[str, Any]]:
        """
        Dla każdej komórki:
        - ustala nagłówek i klucz,
        - wybiera typ kolumny z `columns`,
        - deleguje całą logikę do handlera kolumny.
        """
        record: Dict[str, Any] = {}
        model_fields = self._model_fields()

        for header, cell in row.items():
            # (jeśli parser niesie metadane typu "__row__", pomijamy je)
            if not isinstance(header, str):
                continue
            if header in {"__row__", "_row", "__tr__"}:
                continue

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

            col = (
                    self.columns.get(key) or self.columns.get(header) or self.default_column
            )
            col.apply(ctx, record)

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
