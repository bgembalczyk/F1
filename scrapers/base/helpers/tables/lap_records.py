"""Helper table scraper for lap record tables."""

from __future__ import annotations

import re
from typing import Any, Dict, List

from bs4 import BeautifulSoup, Tag

from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.date import DateColumn
from scrapers.base.table.columns.types.driver import DriverColumn
from scrapers.base.table.columns.types.time import TimeColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper

from scrapers.base.helpers.value_objects import LapRecord


class LapRecordsTableScraper(F1TableScraper):
    """
    Lekki scraper pojedynczej tabeli z rekordami okrążeń.

    Używany tylko jako helper w F1SingleCircuitScraper – korzystamy z całej
    logiki kolumn / ColumnContext / extract_links_from_cell itd.
    """

    CONFIG = ScraperConfig(
        url="https://example.com",
        section_id=None,
        expected_headers=["Time"],
        column_map={
            "Category": "category",
            "Class": "class_",
            "Driver": "driver",
            "Driver/Rider": "driver_rider",
            "Vehicle": "vehicle",
            "Event": "event",
            "Time": "time",
            "Date": "date",
        },
        columns={
            "category": AutoColumn(),
            "class_": AutoColumn(),
            "driver": DriverColumn(),
            "driver_rider": DriverColumn(),
            "vehicle": AutoColumn(),
            "event": UrlColumn(),
            "time": TimeColumn(),
            "date": DateColumn(),
        },
    )

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Nie używamy standardowego fetch()/_parse_soup – w F1SingleCircuitScraper
        sami podajemy konkretne tabele i nagłówki i wołamy parse_row().
        Metoda zostaje tylko po to, żeby klasa była kompletna.
        """
        raise NotImplementedError(
            "LapRecordsTableScraper nie jest używany bezpośrednio – "
            "korzystaj z parse_row()/parse_multi_row() na konkretnych tabelach."
        )

    @staticmethod
    def _split_cell_on_br(cell: Tag) -> List[Tag]:
        """
        Dzieli komórkę na segmenty po <br>. Jeśli nie ma <br>, zwraca [cell].

        Każdy segment jest nowym sztucznym <span>, żeby można było niezależnie
        liczyć tekst i linki (bez grzebania w oryginalnym drzewie DOM).
        """
        html = cell.decode_contents()
        parts = re.split(r"<br\s*/?>", html, flags=re.IGNORECASE)

        segments: List[Tag] = []
        soup = cell.soup or BeautifulSoup("", "html.parser")

        for part in parts:
            if not part.strip():
                continue
            frag_soup = BeautifulSoup(part, "html.parser")
            span = soup.new_tag("span")
            for el in list(frag_soup.contents):
                span.append(el)
            segments.append(span)

        return segments or [cell]

    def parse_multi_row(
        self,
        row: Tag,
        cells: List[Tag],
        headers: List[str],
        *,
        as_value_objects: bool = False,
    ) -> List[Any]:
        """
        Z jednego <tr> zwraca 1..N rekordów.

        Domyślnie zwraca list[dict[str, Any]] (bezpieczne dla JSON).
        Jeśli as_value_objects=True i LapRecord jest dostępny → list[LapRecord].
        """
        _ = row  # API zgodne z innymi helperami; tu nie jest potrzebne

        per_cell_segments: List[List[Tag]] = []
        max_segments = 1

        for cell in cells:
            segs = self._split_cell_on_br(cell)
            per_cell_segments.append(segs)
            max_segments = max(max_segments, len(segs))

        out_records: List[Any] = []

        for idx in range(max_segments):
            seg_cells = [
                segs[idx] if idx < len(segs) else segs[-1] for segs in per_cell_segments
            ]
            record = self.pipeline.parse_cells(headers, seg_cells)

            # Mapowanie do modelu (jeśli ktoś kiedyś doda model_class)
            if self.model_class:
                model = self.model_class(**record)
                if hasattr(model, "model_dump"):
                    record = model.model_dump()
                elif hasattr(model, "dict"):
                    record = model.dict()

            if as_value_objects:
                if LapRecord is None:
                    raise RuntimeError(
                        "as_value_objects=True, ale LapRecord nie jest dostępny w projekcie."
                    )
                out_records.append(LapRecord.from_dict(record))
            else:
                out_records.append(record)

        return out_records

    def headers_match(self, headers: list[str]) -> bool:
        """Sprawdza czy nagłówki zawierają wymagane expected_headers (po normalizacji)."""
        if not self.expected_headers:
            return True
        normalized = {self._normalize_header(h) for h in headers}
        expected = {self._normalize_header(h) for h in self.expected_headers}
        return expected.issubset(normalized)