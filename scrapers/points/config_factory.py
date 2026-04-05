from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.base.factory.record_factory import MappingRecordFactory
from scrapers.base.table.columns.types import AutoColumn
from scrapers.base.table.columns.types import IntColumn
from scrapers.base.table.columns.types import SeasonsColumn
from scrapers.base.table.columns.types import SkipColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.config import build_scraper_config
from scrapers.base.table.dsl.column import ColumnSpec
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.points.base_points_scraper import BasePointsScraper
from scrapers.points.columns.first_place import FirstPlaceColumn
from scrapers.points.constants import HISTORICAL_POSITIONS
from scrapers.points.constants import POINTS_CONSTRUCTORS_CHAMPIONSHIP_HEADER
from scrapers.points.constants import POINTS_DRIVERS_CHAMPIONSHIP_HEADER
from scrapers.points.constants import POINTS_FASTEST_LAP_HEADER
from scrapers.points.constants import POINTS_NOTES_HEADER
from scrapers.points.constants import POINTS_SCORING_HISTORY_EXPECTED_HEADERS
from scrapers.points.constants import POINTS_SEASONS_HEADER

if TYPE_CHECKING:
    from collections.abc import Sequence


def build_points_scoring_systems_history_config(
    *,
    columns: Sequence[ColumnSpec],
) -> ScraperConfig:
    return build_scraper_config(
        url=BasePointsScraper.BASE_URL,
        section_id="Points_scoring_systems",
        expected_headers=POINTS_SCORING_HISTORY_EXPECTED_HEADERS,
        schema=TableSchemaDSL(columns=columns),
        record_factory=MappingRecordFactory(),
    )


def build_points_scoring_systems_history_columns() -> list[ColumnSpec]:
    schema_columns: list[ColumnSpec] = [
        ColumnSpec(POINTS_SEASONS_HEADER, "seasons", SeasonsColumn()),
    ]
    for index, position in enumerate(HISTORICAL_POSITIONS):
        column_instance = FirstPlaceColumn() if index == 0 else IntColumn()
        schema_columns.append(ColumnSpec(position, position.lower(), column_instance))
    schema_columns.extend(
        [
            ColumnSpec(POINTS_FASTEST_LAP_HEADER, "fastest_lap", IntColumn()),
            ColumnSpec(
                POINTS_DRIVERS_CHAMPIONSHIP_HEADER,
                "drivers_championship",
                AutoColumn(),
            ),
            ColumnSpec(
                "Towards WDC",
                "drivers_championship",
                AutoColumn(),
            ),
            ColumnSpec(
                POINTS_CONSTRUCTORS_CHAMPIONSHIP_HEADER,
                "constructors_championship",
                AutoColumn(),
            ),
            ColumnSpec(
                "Towards WCC",
                "constructors_championship",
                AutoColumn(),
            ),
            ColumnSpec(POINTS_NOTES_HEADER, "notes", SkipColumn()),
        ],
    )
    return schema_columns


POINTS_SCORING_SYSTEMS_HISTORY_COLUMNS = build_points_scoring_systems_history_columns()
POINTS_SCORING_SYSTEMS_HISTORY_CONFIG = build_points_scoring_systems_history_config(
    columns=POINTS_SCORING_SYSTEMS_HISTORY_COLUMNS,
)
