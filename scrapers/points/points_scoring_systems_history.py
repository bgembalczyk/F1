from pathlib import Path

from scrapers.base.helpers.runner import run_and_export
from scrapers.base.options import ScraperOptions
from scrapers.base.records import record_from_mapping
from scrapers.base.runner import RunConfig
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl import TableSchemaDSL, column
from scrapers.base.table.scraper import F1TableScraper
from scrapers.base.transformers.points_scoring_systems_history import (
    PointsScoringSystemsHistoryTransformer,
)
from scrapers.points.columns.first_place import FirstPlaceColumn
from scrapers.points.constants import (
    CONSTRUCTORS_CHAMPIONSHIP_HEADER,
    DRIVERS_CHAMPIONSHIP_HEADER,
    FASTEST_LAP_HEADER,
    HISTORICAL_POSITIONS,
    NOTES_HEADER,
    POINTS_SCORING_HISTORY_EXPECTED_HEADERS,
    SEASONS_HEADER,
)


class PointsScoringSystemsHistoryScraper(F1TableScraper):
    """
    Tabela: List of Formula One World Championship points scoring systems used throughout history
    https://en.wikipedia.org/wiki/List_of_Formula_One_World_Championship_points_scoring_systems
    """

    schema_columns = [column(SEASONS_HEADER, "seasons", SeasonsColumn())]
    for index, position in enumerate(HISTORICAL_POSITIONS):
        column_instance = FirstPlaceColumn() if index == 0 else IntColumn()
        schema_columns.append(column(position, position.lower(), column_instance))
    schema_columns.extend(
        [
            column(FASTEST_LAP_HEADER, "fastest_lap", IntColumn()),
            column(DRIVERS_CHAMPIONSHIP_HEADER, "drivers_championship", AutoColumn()),
            column(
                CONSTRUCTORS_CHAMPIONSHIP_HEADER,
                "constructors_championship",
                AutoColumn(),
            ),
            column(NOTES_HEADER, "notes", SkipColumn()),
        ]
    )

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_World_Championship_points_scoring_systems",
        section_id="Points_scoring_systems",
        expected_headers=POINTS_SCORING_HISTORY_EXPECTED_HEADERS,
        schema=TableSchemaDSL(columns=schema_columns),
        record_factory=record_from_mapping,
    )

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        config: ScraperConfig | None = None,
    ) -> None:
        options = options or ScraperOptions()
        options.transformers = list(options.transformers or []) + [
            PointsScoringSystemsHistoryTransformer(),
        ]
        super().__init__(options=options, config=config)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--quality-report",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Zapisz raport jakości do debug_dir/quality_report.json.",
    )
    parser.add_argument(
        "--error-report",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Zapisz raporty błędów do debug_dir/errors.jsonl.",
    )
    args = parser.parse_args()
    run_and_export(
        PointsScoringSystemsHistoryScraper,
        "points/points_scoring_systems_history.json",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
            debug_dir=Path("../../data/debug"),
            quality_report=args.quality_report,
            error_report=args.error_report,
        ),
    )
