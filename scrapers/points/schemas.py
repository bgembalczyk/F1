from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.dsl import TableSchemaDSL
from scrapers.base.table.dsl import column
from scrapers.points.constants import HISTORICAL_POSITIONS
from scrapers.points.constants import POINTS_FASTEST_LAP_HEADER
from scrapers.points.constants import POINTS_NOTES_HEADER
from scrapers.points.constants import POINTS_RACE_LENGTH_COMPLETED_HEADER
from scrapers.points.constants import POINTS_SEASONS_HEADER
from scrapers.points.constants import SPRINT_POSITIONS


def build_shortened_race_points_schema() -> TableSchemaDSL:
    columns = [
        column(POINTS_SEASONS_HEADER, "seasons", SeasonsColumn()),
        column(
            POINTS_RACE_LENGTH_COMPLETED_HEADER,
            "race_length_completed",
            TextColumn(),
        ),
    ]
    columns.extend(
        [
            column(position, position.lower(), AutoColumn())
            for position in HISTORICAL_POSITIONS
        ],
    )
    columns.extend(
        [
            column(POINTS_FASTEST_LAP_HEADER, "fastest_lap", AutoColumn()),
            column(POINTS_NOTES_HEADER, "notes", SkipColumn()),
        ],
    )
    return TableSchemaDSL(columns=columns)


def build_sprint_qualifying_schema() -> TableSchemaDSL:
    columns = [column(POINTS_SEASONS_HEADER, "seasons", SeasonsColumn())]
    columns.extend(
        [
            column(position, position.lower(), IntColumn())
            for position in SPRINT_POSITIONS
        ],
    )
    return TableSchemaDSL(columns=columns)
