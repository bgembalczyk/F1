from __future__ import annotations

from typing import Final
from typing import Literal
from typing import get_args

SeedName = Literal[
    "circuits",
    "constructors_current",
    "constructors_former",
    "constructors_indianapolis_only",
    "constructors_privateer",
    "drivers",
    "drivers_female",
    "drivers_fatalities",
    "engines_indianapolis_only",
    "engines_manufacturers",
    "engines_regulations",
    "engines_restrictions",
    "grands_prix_by_title",
    "grands_prix_red_flagged_non_championship",
    "grands_prix_red_flagged_world_championship",
    "points_history",
    "points_shortened",
    "points_sprint",
    "seasons",
    "sponsorship_liveries",
    "tyres",
]

DomainName = Literal[
    "circuits",
    "constructors",
    "drivers",
    "engines",
    "grands_prix",
    "points",
    "races",
    "rules",
    "seasons",
    "teams",
    "chassis_constructors",
]

LegacyWikiMode = Literal["layer0", "layer1", "full"]
ConstructorStatus = Literal["active", "former"]

CONSTRUCTOR_STATUS_ACTIVE: Final[ConstructorStatus] = "active"
CONSTRUCTOR_STATUS_FORMER: Final[ConstructorStatus] = "former"
WIKI_MODE_VALUES: Final[tuple[LegacyWikiMode, ...]] = get_args(LegacyWikiMode)
