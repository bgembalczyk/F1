from typing import Optional
from typing import TypedDict

from models.records.link import LinkRecord
from models.scrape_types.season_ref_payload import SeasonRefPayload


class ConstructorRow(TypedDict, total=False):
    constructor: LinkRecord
    engine: list[LinkRecord]
    licensed_in: Optional[str | LinkRecord | list[LinkRecord]]
    based_in: list[LinkRecord]
    team: str
    team_url: Optional[str]
    seasons: list[SeasonRefPayload]
    races_entered: Optional[int]
    races_started: Optional[int]
    drivers: Optional[int]
    total_entries: Optional[int]
    wins: Optional[int]
    points: Optional[int]
    poles: Optional[int]
    fastest_laps: Optional[int]
    podiums: Optional[int]
    wcc_titles: Optional[int]
    wdc_titles: Optional[int]
    antecedent_teams: list[LinkRecord]
