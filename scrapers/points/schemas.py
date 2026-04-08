from scrapers.base.table.columns import types as col
from scrapers.base.table.dsl.column import ColumnSpec
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.points import constants


def build_shortened_race_points_schema() -> TableSchemaDSL:
    columns = [
        ColumnSpec(constants.POINTS_SEASONS_HEADER, "seasons", col.SeasonsColumn()),
        ColumnSpec(
            constants.POINTS_RACE_LENGTH_COMPLETED_HEADER,
            "race_length_completed",
            col.TextColumn(),
        ),
    ]
    columns += [
        ColumnSpec(position, position.lower(), col.AutoColumn())
        for position in constants.HISTORICAL_POSITIONS
    ]
    columns.extend(
        [
            ColumnSpec(constants.POINTS_FASTEST_LAP_HEADER, "fastest_lap", col.AutoColumn()),
            ColumnSpec(constants.POINTS_NOTES_HEADER, "notes", col.SkipColumn()),
        ],
    )
    return TableSchemaDSL(columns=columns)


def build_sprint_qualifying_schema() -> TableSchemaDSL:
    columns = [ColumnSpec(constants.POINTS_SEASONS_HEADER, "seasons", col.SeasonsColumn())]
    columns += [
        ColumnSpec(position, position.lower(), col.IntColumn())
        for position in constants.SPRINT_POSITIONS
    ]
    return TableSchemaDSL(columns=columns)
