from typing import TypedDict

from models.scrape_types.season_ref_payload import SeasonRefPayload


class DriverChampionshipsPayload(TypedDict):
    count: int
    seasons: list[SeasonRefPayload]
