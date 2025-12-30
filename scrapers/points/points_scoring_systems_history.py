import re
from pathlib import Path

from scrapers.base.runner import RunConfig
from scrapers.base.runner import run_and_export

from scrapers.base.helpers.parsing import parse_int_from_text
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper
from scrapers.points.constants import HISTORICAL_POSITIONS


class PointsScoringSystemsHistoryScraper(F1TableScraper):
    """
    Tabela: List of Formula One World Championship points scoring systems used throughout history
    https://en.wikipedia.org/wiki/List_of_Formula_One_World_Championship_points_scoring_systems
    """

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_World_Championship_points_scoring_systems",
        section_id="Points_scoring_systems",
        expected_headers=[
            "Seasons",
            *HISTORICAL_POSITIONS,
            "Fastest lap",
            "Drivers' Championship",
            "Constructors' Championship",
            "Notes",
        ],
        column_map={
            "Seasons": "seasons",
            **{position: position.lower() for position in HISTORICAL_POSITIONS},
            "Fastest lap": "fastest_lap",
            "Drivers' Championship": "drivers_championship",
            "Constructors' Championship": "constructors_championship",
            "Notes": "notes",
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
    )

    @staticmethod
    def to_export_records(records: list[dict]) -> list[dict]:
        merged: list[dict] = []
        merged_by_seasons: dict[tuple | None, dict] = {}

        for record in records:
            first_place = record.get("1st")
            role, value = _extract_first_place_role(first_place)
            key = _seasons_key(record.get("seasons"))

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


class FirstPlaceColumn(BaseColumn):
    _ROLE_PATTERN = re.compile(r"\(\s*([dc])\s*\)", re.IGNORECASE)

    def parse(self, ctx: ColumnContext) -> int | dict | None:
        value = parse_int_from_text(ctx.clean_text)
        if value is None:
            return None

        role_match = self._ROLE_PATTERN.search(ctx.clean_text)
        if role_match:
            role = "driver" if role_match.group(1).lower() == "d" else "constructor"
            return {"value": value, "role": role}

        return value


def _seasons_key(seasons: list[dict] | None) -> tuple | None:
    if not seasons:
        return None
    return tuple((season.get("year"), season.get("url")) for season in seasons)


def _extract_first_place_role(first_place: object) -> tuple[str | None, int | None]:
    if isinstance(first_place, dict) and "role" in first_place:
        return first_place.get("role"), first_place.get("value")
    return None, first_place if isinstance(first_place, int) else None


if __name__ == "__main__":
    run_and_export(
        PointsScoringSystemsHistoryScraper,
        "points/points_scoring_systems_history.json",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
