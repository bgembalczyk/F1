from __future__ import annotations

from typing import TYPE_CHECKING

from models.records.factories.mapping import MappingRecordFactory
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.column_factory import IntColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.config import ScraperConfig as TableScraperConfig
from scrapers.base.table.config import build_scraper_config
from scrapers.base.table.dsl.column import ColumnSpec
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.constants.shared_headers import SHARED_SEASONS_HEADER
from scrapers.points.base_points_scraper import BasePointsScraper
from scrapers.points.columns_points.first_place import FirstPlaceColumn

if TYPE_CHECKING:
    from collections.abc import Sequence


def build_points_scoring_systems_history_config(
    *,
    columns: Sequence[ColumnSpec],
) -> TableScraperConfig:
    return build_scraper_config(
        url=BasePointsScraper.BASE_URL,
        section_id="Points_scoring_systems",
        expected_headers=constants.POINTS_SCORING_HISTORY_EXPECTED_HEADERS,
        schema=TableSchemaDSL(columns=columns),
        record_factory=MappingRecordFactory(),
    )


def build_points_scoring_systems_history_columns() -> list[ColumnSpec]:
    schema_columns: list[ColumnSpec] = [
        ColumnSpec(SHARED_SEASONS_HEADER, "seasons", SeasonsColumn()),
    ]
    for index, position in enumerate(constants.HISTORICAL_POSITIONS):
        column_instance = FirstPlaceColumn() if index == 0 else IntColumn()
        schema_columns.append(ColumnSpec(position, position.lower(), column_instance))
    schema_columns.extend(
        [
            ColumnSpec(constants.POINTS_FASTEST_LAP_HEADER, "fastest_lap", IntColumn()),
            ColumnSpec(
                constants.POINTS_DRIVERS_CHAMPIONSHIP_HEADER,
                "drivers_championship",
                AutoColumn(),
            ),
            ColumnSpec(
                "Towards WDC",
                "drivers_championship",
                AutoColumn(),
            ),
            ColumnSpec(
                constants.POINTS_CONSTRUCTORS_CHAMPIONSHIP_HEADER,
                "constructors_championship",
                AutoColumn(),
            ),
            ColumnSpec(
                "Towards WCC",
                "constructors_championship",
                AutoColumn(),
            ),
            ColumnSpec(constants.POINTS_NOTES_HEADER, "notes", SkipColumn()),
        ],
    )
    return schema_columns


POINTS_SCORING_SYSTEMS_HISTORY_COLUMNS = build_points_scoring_systems_history_columns()
POINTS_SCORING_SYSTEMS_HISTORY_CONFIG = build_points_scoring_systems_history_config(
    columns=POINTS_SCORING_SYSTEMS_HISTORY_COLUMNS,
)
