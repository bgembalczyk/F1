from __future__ import annotations

from abc import ABC
from dataclasses import asdict, fields, is_dataclass
from typing import Optional, Sequence, Mapping, List, Dict, Any

from bs4 import BeautifulSoup, Tag

from scrapers.base.helpers.utils import clean_wiki_text, extract_links_from_cell
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.helpers.wiki import extract_links_from_cell, find_section_elements
from scrapers.base.scraper import F1Scraper
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.registry import resolve_column_type
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.base.table.parser import HtmlTableParser


class F1TableScraper(F1Scraper, ABC):
    """
    Scraper oparty o pojedynczą tabelę 'wikitable'.

    Konfiguracja przez pola klasowe:

    - section_id    – id nagłówka sekcji (np. "Constructors_for_the_2025_season"),
                       jeśli None – szukamy po całej stronie.
    - expected_headers – lista nagłówków, które MUSZĄ wystąpić w tabeli (podzbiór).
    - column_map    – mapowanie "nagłówek z tabeli" -> "klucz w dict".
    - columns       – mapowanie klucza/nagłówka -> BaseColumn
                      (MultiColumn / FuncColumn / TextColumn / IntColumn / ...).
    """

    _SKIP = object()

    section_id: Optional[str] = None
    expected_headers: Sequence[str] | None = None
    column_map: Mapping[str, str] = {}

    # klucz (po column_map) lub nagłówek -> BaseColumn
    columns: Mapping[str, BaseColumn] = {}

    table_css_class: str = "wikitable"

    model_class: type | None = None

    # domyślna kolumna dla pól, które nie mają przypisanej logiki
    default_column: BaseColumn = AutoColumn()

    # --- szablon parsowania ---

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
