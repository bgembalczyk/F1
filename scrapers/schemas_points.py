from scrapers.columns.factory import IntColumn
from scrapers.columns.spec import ColumnSpec
from scrapers.columns.types.auto import AutoColumn
from scrapers.columns.types.seasons import SeasonsColumn
from scrapers.columns.types.skip import SkipColumn
from scrapers.columns.types.text import TextColumn
from scrapers.constants.constants_points import HISTORICAL_POSITIONS
from scrapers.constants.constants_points import POINTS_FASTEST_LAP_HEADER
from scrapers.constants.constants_points import POINTS_NOTES_HEADER
from scrapers.constants.constants_points import POINTS_RACE_LENGTH_COMPLETED_HEADER
from scrapers.constants.constants_points import SPRINT_POSITIONS
from scrapers.constants.shared_headers import SHARED_SEASONS_HEADER
from scrapers.table_schema_dsl import TableSchemaDSL


def build_shortened_race_points_schema() -> TableSchemaDSL:
    columns = [
        ColumnSpec(SHARED_SEASONS_HEADER, "seasons", SeasonsColumn()),
        ColumnSpec(
            POINTS_RACE_LENGTH_COMPLETED_HEADER,
            "race_length_completed",
            TextColumn(),
        ),
    ]
    columns += [
        ColumnSpec(position, position.lower(), AutoColumn())
        for position in HISTORICAL_POSITIONS
    ]
    columns.extend(
        [
            ColumnSpec(
                POINTS_FASTEST_LAP_HEADER,
                "fastest_lap",
                AutoColumn(),
            ),
            ColumnSpec(POINTS_NOTES_HEADER, "notes", SkipColumn()),
        ],
    )
    return TableSchemaDSL(columns=columns)


def build_sprint_qualifying_schema() -> TableSchemaDSL:
    columns = [
        ColumnSpec(SHARED_SEASONS_HEADER, "seasons", SeasonsColumn()),
    ]
    columns += [
        ColumnSpec(position, position.lower(), IntColumn())
        for position in SPRINT_POSITIONS
    ]
    return TableSchemaDSL(columns=columns)
