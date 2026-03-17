from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.points.constants import HISTORICAL_POSITIONS
from scrapers.points.constants import POINTS_CONSTRUCTORS_CHAMPIONSHIP_HEADER
from scrapers.points.constants import POINTS_DRIVERS_CHAMPIONSHIP_HEADER
from scrapers.points.constants import POINTS_FASTEST_LAP_HEADER
from scrapers.points.constants import POINTS_NOTES_HEADER
from scrapers.points.constants import POINTS_RACE_LENGTH_COMPLETED_HEADER
from scrapers.points.constants import POINTS_SEASONS_HEADER
from scrapers.points.constants import SPRINT_POSITIONS
from scrapers.points.columns.first_place import FirstPlaceColumn


def build_shortened_race_points_schema() -> TableSchemaDSL:
    columns = [
        column(POINTS_SEASONS_HEADER, "seasons", SeasonsColumn()),
        column(
            POINTS_RACE_LENGTH_COMPLETED_HEADER,
            "race_length_completed",
            TextColumn(),
        ),
    ]
    columns += [
        column(position, position.lower(), AutoColumn())
        for position in HISTORICAL_POSITIONS
    ]
    columns.extend(
        [
            column(POINTS_FASTEST_LAP_HEADER, "fastest_lap", AutoColumn()),
            column(POINTS_NOTES_HEADER, "notes", SkipColumn()),
        ],
    )
    return TableSchemaDSL(columns=columns)


def build_sprint_qualifying_schema() -> TableSchemaDSL:
    columns = [column(POINTS_SEASONS_HEADER, "seasons", SeasonsColumn())]
    columns += [
        column(position, position.lower(), IntColumn()) for position in SPRINT_POSITIONS
    ]
    return TableSchemaDSL(columns=columns)


def build_points_scoring_history_schema() -> TableSchemaDSL:
    columns = [column(POINTS_SEASONS_HEADER, "seasons", SeasonsColumn())]
    columns += [
        column(
            position,
            position.lower(),
            FirstPlaceColumn() if index == 0 else IntColumn(),
        )
        for index, position in enumerate(HISTORICAL_POSITIONS)
    ]
    columns.extend(
        [
            column(POINTS_FASTEST_LAP_HEADER, "fastest_lap", IntColumn()),
            column(
                POINTS_DRIVERS_CHAMPIONSHIP_HEADER,
                "drivers_championship",
                AutoColumn(),
            ),
            column(
                POINTS_CONSTRUCTORS_CHAMPIONSHIP_HEADER,
                "constructors_championship",
                AutoColumn(),
            ),
            column(POINTS_NOTES_HEADER, "notes", SkipColumn()),
        ],
    )
    return TableSchemaDSL(columns=columns)
