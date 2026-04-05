"""DEPRECATED ENTRYPOINT: use scrapers.drivers.entrypoint.run_list_scraper."""

from typing import Any

from scrapers.base.factory.record_factory import RECORD_FACTORIES
from scrapers.base.options import ScraperOptions
from scrapers.base.source_catalog import DRIVERS_LIST
from scrapers.base.table.builders import MetricColumnSpec
from scrapers.base.table.builders import build_columns
from scrapers.base.table.builders import build_metric_columns
from scrapers.base.table.builders import build_name_status_fragment
from scrapers.base.table.columns.types import SeasonsColumn
from scrapers.base.table.columns.types import TextColumn
from scrapers.base.table.config import build_scraper_config
from scrapers.base.table.dsl.column import ColumnSpec
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.base.table.seed_list_scraper import SeedListTableScraper
from scrapers.base.transformers.drivers_championships import (
    DriversChampionshipsTransformer,
)
from scrapers.drivers.columns.driver_name_status import DriverNameStatusColumn
from scrapers.drivers.constants import DRIVER_CHAMPIONSHIPS_HEADER
from scrapers.drivers.constants import DRIVER_FASTEST_LAPS_HEADER
from scrapers.drivers.constants import DRIVER_NAME_HEADER
from scrapers.drivers.constants import DRIVER_NATIONALITY_HEADER
from scrapers.drivers.constants import DRIVER_PODIUMS_HEADER
from scrapers.drivers.constants import DRIVER_POINTS_HEADER
from scrapers.drivers.constants import DRIVER_POLE_POSITIONS_HEADER
from scrapers.drivers.constants import DRIVER_RACE_ENTRIES_HEADER
from scrapers.drivers.constants import DRIVER_RACE_STARTS_HEADER
from scrapers.drivers.constants import DRIVER_RACE_WINS_HEADER
from scrapers.drivers.constants import DRIVER_SEASONS_COMPETED_HEADER
from scrapers.drivers.constants import DRIVERS_LIST_HEADERS
from scrapers.wiki.parsers.elements.wiki_table.base import WikiTableBaseParser
from scrapers.wiki.parsers.sections.section import SectionParser


class DriversListTableParser(WikiTableBaseParser):
    table_type = "drivers_list"
    missing_columns_policy = "ignore"
    extra_columns_policy = "ignore"

    _column_mapping = {
        DRIVER_NAME_HEADER: "driver",
        DRIVER_NATIONALITY_HEADER: "nationality",
        DRIVER_SEASONS_COMPETED_HEADER: "seasons_competed",
        DRIVER_CHAMPIONSHIPS_HEADER: "drivers_championships",
        DRIVER_RACE_ENTRIES_HEADER: "race_entries",
        DRIVER_RACE_STARTS_HEADER: "race_starts",
        DRIVER_POLE_POSITIONS_HEADER: "pole_positions",
        DRIVER_RACE_WINS_HEADER: "race_wins",
        DRIVER_PODIUMS_HEADER: "podiums",
        DRIVER_FASTEST_LAPS_HEADER: "fastest_laps",
        DRIVER_POINTS_HEADER: "points",
    }

    def matches(self, headers: list[str], _table_data: dict[str, Any]) -> bool:
        required_headers = set(DRIVERS_LIST_HEADERS)
        return required_headers.issubset(set(headers))

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        mapped_headers = [
            header for header in headers if header in self._column_mapping
        ]
        driver_headers = [
            header
            for header in mapped_headers
            if self._column_mapping[header] == "driver"
        ]
        other_headers = [
            header
            for header in mapped_headers
            if self._column_mapping[header] != "driver"
        ]
        return {
            header: self._column_mapping[header]
            for header in [*driver_headers, *other_headers]
        }


TABLE_SCHEMA = TableSchemaDSL(
    columns=build_columns(
        build_name_status_fragment(
            header=DRIVER_NAME_HEADER,
            output_key="driver",
            column_type=DriverNameStatusColumn(),
        ),
        [ColumnSpec(DRIVER_NATIONALITY_HEADER, "nationality", TextColumn())],
        [
            ColumnSpec(
                DRIVER_SEASONS_COMPETED_HEADER,
                "seasons_competed",
                SeasonsColumn(),
            ),
        ],
        [
            ColumnSpec(
                DRIVER_CHAMPIONSHIPS_HEADER,
                "drivers_championships",
                TextColumn(),  # zparsujemy ręcznie w fetch()
            ),
        ],
        build_metric_columns(
            [
                MetricColumnSpec(
                    DRIVER_RACE_ENTRIES_HEADER,
                    "race_entries",
                    "races_entered",
                ),
                MetricColumnSpec(
                    DRIVER_RACE_STARTS_HEADER,
                    "race_starts",
                    "races_started",
                ),
                MetricColumnSpec(
                    DRIVER_POLE_POSITIONS_HEADER,
                    "pole_positions",
                    "poles",
                ),
                MetricColumnSpec(DRIVER_RACE_WINS_HEADER, "race_wins", "wins"),
                MetricColumnSpec(DRIVER_PODIUMS_HEADER, "podiums", "podiums"),
                MetricColumnSpec(
                    DRIVER_FASTEST_LAPS_HEADER,
                    "fastest_laps",
                    "fastest_laps",
                ),
                MetricColumnSpec(DRIVER_POINTS_HEADER, "points", "points"),
            ],
            column_overrides={"points": TextColumn()},
        ),
    ),
)


class DriversListSectionParser(SectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._table_parser = DriversListTableParser()

    def parse_group(
        self,
        elements: list,
        *,
        context=None,
    ) -> dict[str, Any]:
        parsed = super().parse_group(elements, context=context)
        self._apply_drivers_table_parser(parsed)
        return parsed

    def _apply_drivers_table_parser(self, payload: dict[str, Any]) -> None:
        for section in payload.get("sub_sections", []):
            self._apply_for_elements(section.get("elements", []))
            self._apply_drivers_table_parser(section)

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


class F1DriversListScraper(SeedListTableScraper):
    domain = "drivers"

    """
    Scraper listy kierowców F1 z:
    https://en.wikipedia.org/wiki/List_of_Formula_One_drivers

    Dodatkowo:
    - is_active: (~ lub * na końcu raw_text w kolumnie "Driver name")
    - is_world_champion: (~ lub ^ na końcu raw_text w kolumnie "Driver name")
    - drivers_championships: parsowane do dict {count, seasons}
    """

    options_profile = "seed_strict"

    CONFIG = build_scraper_config(
        url=DRIVERS_LIST.base_url,
        section_id=DRIVERS_LIST.section_id,
        expected_headers=DRIVERS_LIST_HEADERS,
        schema=TABLE_SCHEMA,
        record_factory=RECORD_FACTORIES.builders("driver"),
    )

    def __init__(self, *, options: ScraperOptions | None = None) -> None:
        super().__init__(options=options)
        parser = DriversListSectionParser()
        self.section_parser = parser
        self.body_content_parser.content_text_parser.section_parser = parser

    def extend_options(self, options: ScraperOptions) -> ScraperOptions:
        new_transformers = [
            *list(options.pipeline.transformers or []),
            DriversChampionshipsTransformer(),
        ]
        options.pipeline.transformers = new_transformers
        options.transformers = new_transformers
        return options
