"""DEPRECATED ENTRYPOINT: use scrapers.drivers.entrypoint.run_list_scraper."""

import warnings

from scrapers.builders_table import MetricColumnSpec
from scrapers.builders_table import build_columns
from scrapers.builders_table import build_metric_columns
from scrapers.builders_table import build_name_status_fragment
from scrapers.columns.spec import ColumnSpec
from scrapers.columns.types.multi.name_status_column.driver import DriverNameStatusColumn
from scrapers.columns.types.seasons import SeasonsColumn
from scrapers.columns.types.text import TextColumn
from scrapers.config_table import build_scraper_config
from scrapers.constants_drivers import DRIVERS_LIST_HEADERS
from scrapers.constants_drivers import DRIVER_CHAMPIONSHIPS_HEADER
from scrapers.constants_drivers import DRIVER_FASTEST_LAPS_HEADER
from scrapers.constants_drivers import DRIVER_NAME_HEADER
from scrapers.constants_drivers import DRIVER_NATIONALITY_HEADER
from scrapers.constants_drivers import DRIVER_PODIUMS_HEADER
from scrapers.constants_drivers import DRIVER_POINTS_HEADER
from scrapers.constants_drivers import DRIVER_POLE_POSITIONS_HEADER
from scrapers.constants_drivers import DRIVER_RACE_ENTRIES_HEADER
from scrapers.constants_drivers import DRIVER_RACE_STARTS_HEADER
from scrapers.constants_drivers import DRIVER_RACE_WINS_HEADER
from scrapers.constants_drivers import DRIVER_SEASONS_COMPETED_HEADER
from scrapers.driver_ordered_table_parser import DriverOrderedTableParser
from scrapers.options import ScraperOptions
from scrapers.parsers.section.protocol import SectionParser
from scrapers.seed_list_scraper_table import SeedListTableScraper
from scrapers.source_catalog import DRIVERS_LIST
from scrapers.table_schema_dsl import TableSchemaDSL
from scrapers.transformers.record.drivers_championships import DriversChampionshipsTransformer

warnings.warn("list_scraper_drivers is deprecated; use scrapers.drivers_list_scraper.", DeprecationWarning, stacklevel=2)


from typing import Any

from scrapers.adapters.factories.dataclass import RECORD_FACTORIES


class DriversListTableParser(DriverOrderedTableParser):
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
                TextColumn(),
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
                MetricColumnSpec(
                    DRIVER_RACE_WINS_HEADER,
                    "race_wins",
                    "wins",
                ),
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
