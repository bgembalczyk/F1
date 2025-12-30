from pathlib import Path

from scrapers.base.runner import RunConfig
from scrapers.base.runner import run_and_export
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper
from scrapers.points.constants import HISTORICAL_POSITIONS


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
        column_map={
            "Seasons": "seasons",
            "Race length completed": "race_length_completed",
            **{position: position.lower() for position in HISTORICAL_POSITIONS},
            "Fastest lap": "fastest_lap",
            "Notes": "notes",
        },
        columns={
            "seasons": SeasonsColumn(),
            "race_length_completed": TextColumn(),
            **{position.lower(): AutoColumn() for position in HISTORICAL_POSITIONS},
            "fastest_lap": AutoColumn(),
            "notes": SkipColumn(),
        },
    )

    @staticmethod
    def to_export_records(records):
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


if __name__ == "__main__":
    run_and_export(
        ShortenedRacePointsScraper,
        "points/points_scoring_systems_shortened.json",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
