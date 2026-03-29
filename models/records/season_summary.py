from typing import TypedDict

from models.records.link import LINK_SCHEMA
from models.records.link import LinkRecord
from validation.schemas import NestedSchema
from validation.schemas import RecordSchema


class SeasonSummaryRecord(TypedDict, total=False):
    season: LinkRecord
    races: int | None
    countries: int | None
    first: LinkRecord | None
    last: LinkRecord | None
    drivers_champion_team: list[LinkRecord]
    constructors_champion: list[LinkRecord]
    winners: int | None


SEASON_SUMMARY_SCHEMA = RecordSchema(
    required=("season", "races", "countries", "drivers_champion_team"),
    types={
        "season": dict,
        "races": int,
        "countries": int,
        "first": dict,
        "last": dict,
        "drivers_champion_team": list,
        "constructors_champion": list,
        "winners": int,
    },
    allow_none=(
        "races",
        "countries",
        "first",
        "last",
        "constructors_champion",
        "winners",
    ),
    nested={
        "season": NestedSchema(LINK_SCHEMA),
        "first": NestedSchema(LINK_SCHEMA),
        "last": NestedSchema(LINK_SCHEMA),
        "drivers_champion_team": NestedSchema(LINK_SCHEMA, is_list=True),
        "constructors_champion": NestedSchema(LINK_SCHEMA, is_list=True),
    },
)
