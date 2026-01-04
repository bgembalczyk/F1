from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.schema import TableSchemaBuilder
from scrapers.points.constants import FASTEST_LAP_HEADER
from scrapers.points.constants import HISTORICAL_POSITIONS
from scrapers.points.constants import NOTES_HEADER
from scrapers.points.constants import RACE_LENGTH_COMPLETED_HEADER
from scrapers.points.constants import SEASONS_HEADER
from scrapers.points.constants import SPRINT_POSITIONS


def build_shortened_race_points_schema() -> TableSchemaBuilder:
    builder = (
        TableSchemaBuilder()
        .map(SEASONS_HEADER, "seasons", SeasonsColumn())
        .map(RACE_LENGTH_COMPLETED_HEADER, "race_length_completed", TextColumn())
    )
    for position in HISTORICAL_POSITIONS:
        builder.map(position, position.lower(), AutoColumn())
    return (
        builder.map(FASTEST_LAP_HEADER, "fastest_lap", AutoColumn()).map(
            NOTES_HEADER,
            "notes",
            SkipColumn(),
        )
    )


def build_sprint_qualifying_schema() -> TableSchemaBuilder:
    builder = TableSchemaBuilder().map(SEASONS_HEADER, "seasons", SeasonsColumn())
    for position in SPRINT_POSITIONS:
        builder.map(position, position.lower(), IntColumn())
    return builder
