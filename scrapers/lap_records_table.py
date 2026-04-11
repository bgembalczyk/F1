"""Helper table scraper for lap record tables."""

from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from models.records.factories.mapping import MappingRecordFactory
from models.value_objects.lap_record import LapRecord
from scrapers.columns.spec import ColumnSpec
from scrapers.columns.types.auto import AutoColumn
from scrapers.columns.types.date import DateColumn
from scrapers.columns.types.driver import DriverColumn
from scrapers.columns.types.time import TimeColumn
from scrapers.columns.types.url import UrlColumn
from scrapers.config_table import build_scraper_config
from scrapers.headers_table import normalize_header
from scrapers.helpers.cell_splitting import split_cell_on_br
from scrapers.scraper_table import F1TableScraper
from scrapers.table_schema_dsl import TableSchemaDSL


class LapRecordsTableScraper(F1TableScraper):
    """
    Lekki scraper pojedynczej tabeli z rekordami okrążeń.

    Używany tylko jako helper w F1SingleCircuitScraper - korzystamy z całej
    logiki kolumn / ColumnContext / extract_links_from_cell itd.
    """

    schema_columns = [
        ColumnSpec("Category", "category", AutoColumn()),
        ColumnSpec("Class", "class_", AutoColumn()),
        ColumnSpec("Driver", "driver", DriverColumn()),
        ColumnSpec("Driver/Rider", "driver_rider", DriverColumn()),
        ColumnSpec("Vehicle", "vehicle", AutoColumn()),
        ColumnSpec("Event", "event", UrlColumn()),
        ColumnSpec("Time", "time", TimeColumn()),
        ColumnSpec("Date", "date", DateColumn()),
    ]

    CONFIG = build_scraper_config(
        url="https://en.wikipedia.org",
        section_id=None,
        expected_headers=["Time"],
        schema=TableSchemaDSL(columns=schema_columns),
        record_factory=MappingRecordFactory(),
    )

    def _parse_soup(self, _soup: BeautifulSoup) -> list[dict[str, Any]]:
        """
        LapRecordsTableScraper nie jest używany bezpośrednio - w
        F1SingleCircuitScraper sami podajemy konkretne tabele i nagłówki
        i wołamy parse_row().
        """
        msg = (
            "LapRecordsTableScraper nie jest używany bezpośrednio - "
            "korzystaj z parse_row()/parse_multi_row() na konkretnych tabelach."
        )
        raise NotImplementedError(
            msg,
        )

    def parse_multi_row(
        self,
        row: Tag,
        cells: list[Tag],
        headers: list[str],
        *,
        as_value_objects: bool = False,
    ) -> list[Any]:
        """
        Z jednego <tr> zwraca 1..N rekordów.

        Domyślnie zwraca list[dict[str, Any]] (bezpieczne dla JSON).
        Jeśli as_value_objects=True i LapRecord jest dostępny → list[LapRecord].
        """
        _ = row  # API zgodne z innymi helperami; tu nie jest potrzebne

        per_cell_segments: list[list[Tag]] = []
        max_segments = 1

        for cell in cells:
            segs = split_cell_on_br(cell)
            per_cell_segments.append(segs)
            max_segments = max(max_segments, len(segs))

        out_records: list[Any] = []

        for idx in range(max_segments):
            seg_cells = [
                segs[idx] if idx < len(segs) else segs[-1] for segs in per_cell_segments
            ]
            record = self.extractor.pipeline.parse_cells(headers, seg_cells)

            if as_value_objects:
                if LapRecord is None:
                    msg = (
                        "as_value_objects=True, ale LapRecord "
                        "nie jest dostępny w projekcie."
                    )
                    raise RuntimeError(
                        msg,
                    )
                out_records.append(LapRecord(data=dict(record)))
            else:
                out_records.append(record)

        return out_records

    def headers_match(self, headers: list[str]) -> bool:
        """Sprawdza, czy nagłówki zawierają wymagane expected_headers.

        Dopasowanie odbywa się po normalizacji.
        """
        if not self.expected_headers:
            return True
        normalized = {normalize_header(h) for h in headers}
        expected = {normalize_header(h) for h in self.expected_headers}
        return expected.issubset(normalized)
