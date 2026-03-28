from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.helpers.normalize import normalize_auto_value
from scrapers.base.records import record_from_mapping
from scrapers.base.sections.interface import SectionParseResult
from scrapers.base.sections.serializer import build_section_metadata
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.driver_list import DriverListColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.base.table.parser import HtmlTableParser
from scrapers.base.table.pipeline import TablePipeline
from scrapers.grands_prix.columns.circuit_location import LocationColumn
from scrapers.grands_prix.columns.constructor_split import ConstructorSplitColumn
from scrapers.grands_prix.helpers.constants import BACKGROUND_HEX
from scrapers.grands_prix.helpers.constants import BACKGROUND_MAP
from scrapers.grands_prix.helpers.constants import DEFAULT_CHAMPIONSHIP
from scrapers.grands_prix.helpers.constants import SHORT_HEX_LEN
from scrapers.grands_prix.helpers.constants import UNKNOWN_CHAMPIONSHIP

if TYPE_CHECKING:
    from bs4 import BeautifulSoup
    from bs4 import Tag


class GrandPrixByYearSectionParser:
    def __init__(
        self,
        *,
        url: str,
        include_urls: bool,
        normalize_empty_values: bool,
    ) -> None:
        self._url = url
        self._include_urls = include_urls
        self._normalize_empty_values = normalize_empty_values

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        pipeline = self._build_pipeline(section_id=None)
        parser = HtmlTableParser(
            section_id=None,
            expected_headers=pipeline.expected_headers,
            section_domain="grands_prix",
        )
        records: list[dict[str, Any]] = []
        for row_index, row in enumerate(parser.parse(section_fragment)):
            record = pipeline.parse_cells(row.headers, row.cells, row_index=row_index)
            if not record or self._is_not_held_record(record):
                continue
            record["championship"] = self._championship_from_row(row.raw_tr)
            records.append(record)
        return SectionParseResult(
            section_id="By_year",
            section_label="By year",
            records=records,
            metadata=build_section_metadata(parser=self.__class__.__name__, source="wikipedia"),
        )

    def _build_pipeline(self, section_id: str | None) -> TablePipeline:
        schema = TableSchemaDSL(
            columns=[
                column("Year", "year", UrlColumn()),
                column("Driver", "driver", DriverListColumn()),
                column("Constructor", "constructor", ConstructorSplitColumn()),
                column("Report", "report", AutoColumn()),
                column("Location", "location", LocationColumn()),
            ],
        )
        config = ScraperConfig(
            url=self._url,
            section_id=section_id,
            expected_headers=["Year", "Driver", "Constructor", "Report"],
            schema=schema,
            record_factory=record_from_mapping,
        )
        return TablePipeline(
            config=config,
            include_urls=self._include_urls,
            normalize_empty_values=self._normalize_empty_values,
        )

    def _championship_from_row(self, row: Tag) -> str:
        color = self._background_color(row)
        if color is None:
            return DEFAULT_CHAMPIONSHIP
        return BACKGROUND_MAP.get(color, UNKNOWN_CHAMPIONSHIP)

    def _background_color(self, row: Tag) -> str | None:
        for candidate in [row.get("style"), row.get("bgcolor")]:
            color = self._extract_color(candidate)
            if color:
                return color
        for cell in row.find_all(["th", "td"], recursive=False):
            for candidate in [cell.get("style"), cell.get("bgcolor")]:
                color = self._extract_color(candidate)
                if color:
                    return color
        return None

    def _extract_color(self, candidate: str | None) -> str | None:
        if not candidate:
            return None
        match = BACKGROUND_HEX.search(candidate)
        if not match:
            return None
        normalized = match.group(1).lower()
        if len(normalized) == SHORT_HEX_LEN:
            return "".join(ch * 2 for ch in normalized)
        return normalized

    def _is_not_held_record(self, record: dict[str, Any]) -> bool:
        report_text = self._get_text(record.get("report"))
        location = record.get("location")
        layout_text = location.get("layout") if isinstance(location, dict) else None
        circuit_text = (
            self._get_text(location.get("circuit"))
            if isinstance(location, dict)
            else None
        )
        driver_text = self._list_text(record.get("driver"))
        chassis_text = self._get_text(record.get("chassis_constructor"))
        engine_text = self._get_text(record.get("engine_constructor"))
        if not all([driver_text, chassis_text, engine_text, circuit_text]):
            return False
        if not (driver_text == chassis_text == engine_text == circuit_text):
            return False
        if driver_text == "Not held":
            return True
        return bool(report_text and report_text.lower().startswith("not held")) or bool(
            layout_text
            and layout_text.lower().startswith(("not held due to", "cancelled due to")),
        )

    @staticmethod
    def _get_text(value: Any) -> str | None:
        normalized = normalize_auto_value(value, strip_marks=True, drop_empty=True)
        if isinstance(normalized, dict):
            text = normalized.get("text")
            return text if isinstance(text, str) and text else None
        if isinstance(normalized, str):
            return normalized or None
        return None

    def _list_text(self, items: Any) -> str | None:
        normalized = normalize_auto_value(items, strip_marks=True, drop_empty=True)
        if not isinstance(normalized, list) or not normalized:
            return None
        first_text = self._get_text(normalized[0])
        if not first_text:
            return None
        return (
            first_text
            if all(self._get_text(item) == first_text for item in normalized)
            else None
        )
