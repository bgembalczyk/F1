from pathlib import Path

from scrapers.base.helpers.runner import run_and_export
from scrapers.base.records import record_from_mapping
from scrapers.base.runner import RunConfig
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper
from scrapers.base.table.schema import TableSchemaBuilder
from scrapers.base.transformers import RecordTransformer
from scrapers.points.constants import HISTORICAL_POSITIONS


class ShortenedRacePointsTransformer(RecordTransformer):
    def transform(self, records: list[dict]) -> list[dict]:
        grouped: list[dict] = []
        index: dict[tuple, int] = {}

        for record in records:
            seasons = record.get("seasons", [])
            key = tuple((season.get("year"), season.get("url")) for season in seasons)
            if key not in index:
                grouped.append(
                    {
                        "seasons": seasons,
                        "race_length_points": [],
                    }
                )
                index[key] = len(grouped) - 1

            grouped[index[key]]["race_length_points"].append(
                {key: value for key, value in record.items() if key != "seasons"}
            )

        return grouped


def _build_shortened_race_points_schema() -> TableSchemaBuilder:
    builder = (
        TableSchemaBuilder()
        .map("Seasons", "seasons", SeasonsColumn())
        .map("Race length completed", "race_length_completed", TextColumn())
    )
    for position in HISTORICAL_POSITIONS:
        builder.map(position, position.lower(), AutoColumn())
    return (
        builder.map("Fastest lap", "fastest_lap", AutoColumn()).map(
            "Notes",
            "notes",
            SkipColumn(),
        )
    )


class ShortenedRacePointsScraper(F1TableScraper):
    """
    Tabela: Shortened race points criteria
    https://en.wikipedia.org/wiki/List_of_Formula_One_World_Championship_points_scoring_systems
    """

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_World_Championship_points_scoring_systems",
        section_id="Shortened_races",
        expected_headers=[
            "Seasons",
            "Race length completed",
            *HISTORICAL_POSITIONS,
            "Fastest lap",
            "Notes",
        ],
        schema=_build_shortened_race_points_schema(),
        record_factory=record_from_mapping,
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.transformers = [ShortenedRacePointsTransformer()]


if __name__ == "__main__":
    run_and_export(
        ShortenedRacePointsScraper,
        "points/points_scoring_systems_shortened.json",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
