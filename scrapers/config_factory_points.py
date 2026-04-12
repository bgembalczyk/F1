from __future__ import annotations

from typing import TYPE_CHECKING

from models.records.factories.mapping import MappingRecordFactory
from scrapers.base_points_scraper import BasePointsScraper
from scrapers.columns.factory import IntColumn
from scrapers.columns.spec import ColumnSpec
from scrapers.columns.types.auto import AutoColumn
from scrapers.columns.types.first_place import FirstPlaceColumn
from scrapers.columns.types.seasons import SeasonsColumn
from scrapers.columns.types.skip import SkipColumn
from scrapers.config_table import TableConfig
from scrapers.config_table import build_scraper_config
from scrapers.constants.shared_headers import SHARED_SEASONS_HEADER
from scrapers.constants_points import HISTORICAL_POSITIONS
from scrapers.constants_points import POINTS_CONSTRUCTORS_CHAMPIONSHIP_HEADER
from scrapers.constants_points import POINTS_DRIVERS_CHAMPIONSHIP_HEADER
from scrapers.constants_points import POINTS_FASTEST_LAP_HEADER
from scrapers.constants_points import POINTS_NOTES_HEADER
from scrapers.constants_points import POINTS_SCORING_HISTORY_EXPECTED_HEADERS
from scrapers.table_schema_dsl import TableSchemaDSL

if TYPE_CHECKING:
    from collections.abc import Sequence


def build_points_scoring_systems_history_config(
    *,
    columns: Sequence[ColumnSpec],
) -> TableConfig:
    return build_scraper_config(
        url=BasePointsScraper.BASE_URL,
        section_id="Points_scoring_systems",
        expected_headers=POINTS_SCORING_HISTORY_EXPECTED_HEADERS,
        schema=TableSchemaDSL(columns=columns),
        record_factory=MappingRecordFactory(),
    )


def build_points_scoring_systems_history_columns() -> list[ColumnSpec]:
    schema_columns: list[ColumnSpec] = [
        ColumnSpec(SHARED_SEASONS_HEADER, "seasons", SeasonsColumn()),
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
