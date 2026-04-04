from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from models.validation.engine_restriction import EngineRestriction
from scrapers.base.factory.record_factory import RECORD_FACTORIES
from scrapers.base.source_catalog import ENGINE_REGULATIONS
from scrapers.base.table.columns.types import LinksListColumn
from scrapers.base.table.columns.types import RangeColumn
from scrapers.base.table.columns.types import SeasonsColumn
from scrapers.base.table.columns.types import UnitColumn
from scrapers.base.table.config import build_scraper_config
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.engines.base_engine_table_scraper import BaseEngineTableScraper
from scrapers.engines.columns.engine_rpm_limit import EngineRpmLimitColumn
from scrapers.engines.columns.fuel_flow_rate import FuelFlowRateColumn
from scrapers.engines.columns.fuel_injection_pressure_limit import (
    FuelInjectionPressureLimitColumn,
)
from scrapers.engines.columns.fuel_limit_per_race import FuelLimitPerRaceColumn
from scrapers.wiki.parsers.elements.wiki_table.base import WikiTableBaseParser
from scrapers.wiki.parsers.sections.section import SectionParser
from scrapers.wiki.parsers.sections.sub_section import SubSectionParser


class EngineRestrictionsTableParser(WikiTableBaseParser):
    table_type = "engine_restrictions"
    missing_columns_policy = "ignore"
    extra_columns_policy = "ignore"

    _column_mapping = {
        "Year": "year",
        "2000-2005": "rules_2000_2005",
        "2006-2013": "rules_2006_2013",
        "2014-2025": "rules_2014_2025",
    }

    def matches(self, headers: list[str], _table_data: dict[str, Any]) -> bool:
        required_headers = {"Year", "2000-2005", "2006-2013", "2014-2025"}
        return required_headers.issubset(set(headers))

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {
            header: self._column_mapping[header]
            for header in headers
            if header in self._column_mapping
        }


TABLE_SCHEMA = TableSchemaDSL(
    columns=[
        column("Year", "year", SeasonsColumn()),
        column("Size", "size", UnitColumn(unit="litre")),
        column("Type of engine", "type_of_engine", LinksListColumn()),
        column(
            "Fuel-limit per race",
            "fuel_limit_per_race",
            FuelLimitPerRaceColumn(),
        ),
        column("Fuel-flow rate", "fuel_flow_rate", FuelFlowRateColumn()),
        column(
            "Fuel-injection pressure limit",
            "fuel_injection_pressure_limit",
            FuelInjectionPressureLimitColumn(),
        ),
        column("Engine RPM limit", "engine_rpm_limit", EngineRpmLimitColumn()),
        column(
            "Power Output",
            "power_output",
            RangeColumn(
                UnitColumn(unit="hp"),
                UnitColumn(unit="hp"),
                shared_suffix="hp",
            ),
        ),
    ],
)


class EngineSubSectionParser(SubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._table_parser = EngineRestrictionsTableParser()

    def parse_group(
        self,
        elements: list,
        *,
        context=None,
    ) -> dict[str, Any]:
        parsed = super().parse_group(elements, context=context)
        self._apply_engine_restrictions_table_parser(parsed)
        return parsed

    def _apply_engine_restrictions_table_parser(self, payload: dict[str, Any]) -> None:
        for section in payload.get("sub_sub_sections", []):
            self._apply_for_elements(section.get("elements", []))
            self._apply_engine_restrictions_table_parser(section)

    def _apply_for_elements(self, elements: list[dict[str, Any]]) -> None:
        for element in elements:
            if element.get("kind") != "table":
                continue
            data = element.get("data")
            if not isinstance(data, dict):
                continue
            parsed = self._table_parser.parse(data)
            if parsed is not None:
                element["data"] = parsed


class CurrentRulesSectionParser(SectionParser):
    def __init__(self) -> None:
        super().__init__()
        self.child_parser = EngineSubSectionParser()


class EngineRestrictionsScraper(BaseEngineTableScraper):
    """
    Ograniczenia silnikowe F1:
    https://en.wikipedia.org/wiki/Formula_One_regulations#Engine
    """

    CONFIG = build_scraper_config(
        url=ENGINE_REGULATIONS.url(),
        section_id=ENGINE_REGULATIONS.section_id,
        expected_headers=["Year", "2000-2005", "2006-2013", "2014-2025"],
        record_factory=RECORD_FACTORIES.callable(EngineRestriction),
        schema=TABLE_SCHEMA,
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        parser = CurrentRulesSectionParser()
        self.section_parser = parser
        self.body_content_parser.content_text_parser.section_parser = parser

    def _parse_soup(self, soup: BeautifulSoup) -> list[Any]:
        """Parse transposed table where years are columns and metrics are rows."""
        table = self._find_table(soup)
        header_row = table.find("tr")
        if not header_row:
            msg = "Nie znaleziono wiersza nagłówkowego w tabeli."
            raise RuntimeError(msg)

        header_cells = header_row.find_all(["th", "td"])
        min_header_cells = 2
        if len(header_cells) < min_header_cells:
            msg = "Nagłówek tabeli jest niekompletny."
            raise RuntimeError(msg)

        year_cells = header_cells[1:]

        # Parse rows to extract labels and cells
        parser = self._create_parser()
        rows = parser.parse(soup)
        row_labels: list[str] = []
        row_cells: list[list[Tag]] = []
        for row in rows:
            if not row.cells:
                continue
            label_cell = row.cells[0]
            cleaned_cells = self._clean_cells([label_cell])
            label = cleaned_cells[0]
            row_labels.append(label)
            row_cells.append(row.cells[1:])

        # Build records by transposing: each year becomes a record
        headers = ["Year", *row_labels]
        records: list[Any] = []
        for index, year_cell in enumerate(year_cells):
            cells: list[Tag] = [year_cell]
            for cells_for_row in row_cells:
                if index < len(cells_for_row):
                    cells.append(cells_for_row[index])
                else:
                    cells.append(soup.new_tag("td"))
            record = self._parse_record(headers, cells, index)
            if record:
                records.append(record)

        return records
