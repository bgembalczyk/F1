from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from models.validation.engine.estriction import EngineRestriction
from scrapers.adapters.factories.dataclass import RECORD_FACTORIES
from scrapers.base_engine_table_scraper import BaseEngineTableScraper
from scrapers.columns.spec import ColumnSpec
from scrapers.columns.types.engine_rpm_limit import EngineRpmLimitColumn
from scrapers.columns.types.fuel_flow_rate import FuelFlowRateColumn
from scrapers.columns.types.fuel_injection_pressure_limit import (
    FuelInjectionPressureLimitColumn,
)
from scrapers.columns.types.fuel_limit_per_race import FuelLimitPerRaceColumn
from scrapers.columns.types.links_list import LinksListColumn
from scrapers.columns.types.range import RangeColumn
from scrapers.columns.types.seasons import SeasonsColumn
from scrapers.columns.types.unit import UnitColumn
from scrapers.config_table import build_scraper_config
from scrapers.parsers.wiki.sections.engine_restrictions_section_parser import CurrentRulesSectionParser
from scrapers.source_catalog import ENGINE_REGULATIONS
from scrapers.table_schema_dsl import TableSchemaDSL

TABLE_SCHEMA = TableSchemaDSL(
    columns=[
        ColumnSpec("Year", "year", SeasonsColumn()),
        ColumnSpec("Size", "size", UnitColumn(unit="litre")),
        ColumnSpec("Type of engine", "type_of_engine", LinksListColumn()),
        ColumnSpec(
            "Fuel-limit per race",
            "fuel_limit_per_race",
            FuelLimitPerRaceColumn(),
        ),
        ColumnSpec("Fuel-flow rate", "fuel_flow_rate", FuelFlowRateColumn()),
        ColumnSpec(
            "Fuel-injection pressure limit",
            "fuel_injection_pressure_limit",
            FuelInjectionPressureLimitColumn(),
        ),
        ColumnSpec("Engine RPM limit", "engine_rpm_limit", EngineRpmLimitColumn()),
        ColumnSpec(
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


class EngineRestrictionsScraper(BaseEngineTableScraper):
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


__all__ = ["EngineRestrictionsScraper", "TABLE_SCHEMA"]
