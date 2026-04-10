from dataclasses import dataclass, field

from models.value_objects.link import Link
from models.value_objects.season_ref import SeasonRef


@dataclass
class HasLink:
    link: Link = field(default_factory=Link)


@dataclass
class HasSeasons:
    seasons: list[SeasonRef] = field(default_factory=list)


@dataclass
class HasStats:
    stats: dict[str, int | float | str | None] = field(default_factory=dict)


@dataclass
class HasStatus:
    status: str | None = None


@dataclass
class HasLocation:
    location: str | None = None


__all__ = [
    "HasLink",
    "HasSeasons",
    "HasStats",
    "HasStatus",
    "HasLocation",
]
