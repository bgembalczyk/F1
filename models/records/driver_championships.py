from typing import TypedDict

from models.records.season import SeasonRecord


class DriversChampionshipsRecord(TypedDict):
    count: int
    seasons: list[SeasonRecord]
