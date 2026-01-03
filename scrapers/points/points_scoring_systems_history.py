from pathlib import Path

from scrapers.base.helpers.runner import run_and_export
from scrapers.base.records import record_from_mapping
from scrapers.base.runner import RunConfig
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper
from scrapers.base.transformers import RecordTransformer
from scrapers.points.constants import (
    CONSTRUCTORS_CHAMPIONSHIP_HEADER,
    DRIVERS_CHAMPIONSHIP_HEADER,
    FASTEST_LAP_HEADER,
    HISTORICAL_POSITIONS,
    NOTES_HEADER,
    POINTS_SCORING_HISTORY_EXPECTED_HEADERS,
    SEASONS_HEADER,
)
from scrapers.points.helpers.columns.first_place import FirstPlaceColumn
from scrapers.points.helpers.parsers import extract_first_place_role
from scrapers.points.helpers.parsers import seasons_key


class PointsScoringSystemsHistoryTransformer(RecordTransformer):
    def transform(self, records: list[dict]) -> list[dict]:
        merged: list[dict] = []
        merged_by_seasons: dict[tuple | None, dict] = {}

        for record in records:
            first_place = record.get("1st")
            role, value = extract_first_place_role(first_place)
            key = seasons_key(record.get("seasons"))

            if role:
                existing = merged_by_seasons.get(key)
                if existing is None:
                    merged_record = dict(record)
                    merged_record["1st"] = {role: value}
                    merged_by_seasons[key] = merged_record
                    merged.append(merged_record)
                else:
                    merged_first = existing.get("1st")
                    merged_first = (
                        dict(merged_first) if isinstance(merged_first, dict) else {}
                    )
                    merged_first[role] = value
                    existing["1st"] = merged_first
                continue

            if key not in merged_by_seasons:
                merged_by_seasons[key] = record
                merged.append(record)

        return merged


class PointsScoringSystemsHistoryScraper(F1TableScraper):
    """
    Tabela: List of Formula One World Championship points scoring systems used throughout history
    https://en.wikipedia.org/wiki/List_of_Formula_One_World_Championship_points_scoring_systems
    """

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_World_Championship_points_scoring_systems",
        section_id="Points_scoring_systems",
        expected_headers=POINTS_SCORING_HISTORY_EXPECTED_HEADERS,
        column_map={
            SEASONS_HEADER: "seasons",
            **{position: position.lower() for position in HISTORICAL_POSITIONS},
            FASTEST_LAP_HEADER: "fastest_lap",
            DRIVERS_CHAMPIONSHIP_HEADER: "drivers_championship",
            CONSTRUCTORS_CHAMPIONSHIP_HEADER: "constructors_championship",
            NOTES_HEADER: "notes",
        },
        columns={
            "seasons": SeasonsColumn(),
            "1st": FirstPlaceColumn(),
            **{position.lower(): IntColumn() for position in HISTORICAL_POSITIONS[1:]},
            "fastest_lap": IntColumn(),
            "drivers_championship": AutoColumn(),
            "constructors_championship": AutoColumn(),
            "notes": SkipColumn(),
        },
        record_factory=record_from_mapping,
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.transformers = [PointsScoringSystemsHistoryTransformer()]


if __name__ == "__main__":
    run_and_export(
        PointsScoringSystemsHistoryScraper,
        "points/points_scoring_systems_history.json",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
