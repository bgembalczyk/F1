from __future__ import annotations

from enum import Enum

from scrapers.wiki.constants import FORMER_CONSTRUCTORS_SOURCE
from scrapers.wiki.constants import INDIANAPOLIS_ONLY_CONSTRUCTORS_SOURCE
from scrapers.wiki.constants import TYRE_MANUFACTURERS_SOURCE


class DomainName(str, Enum):
    DRIVERS = "drivers"
    CONSTRUCTORS = "constructors"
    CHASSIS_CONSTRUCTORS = "chassis_constructors"
    CIRCUITS = "circuits"
    SEASONS = "seasons"
    GRANDS_PRIX = "grands_prix"
    ENGINES = "engines"
    POINTS = "points"
    SPONSORSHIP_LIVERIES = "sponsorship_liveries"
    TYRES = "tyres"
    TEAMS = "teams"
    RACES = "races"
    RULES = "rules"
    CONSTRUCTOR = "constructor"
    CHASSIS = "chassis"
    ANY = "*"

    @classmethod
    def from_io(cls, value: str) -> "DomainName":
        return cls(value)

    def __str__(self) -> str:
        return self.value


class LayerName(str, Enum):
    LIST = "list"
    SECTIONS = "sections"
    INFOBOX = "infobox"
    POSTPROCESS = "postprocess"
    LAYER_ONE = "layer_one"

    @classmethod
    def from_io(cls, value: str) -> "LayerName":
        return cls(value)

    def __str__(self) -> str:
        return self.value


class KeySourceName(str, Enum):
    FORMER_CONSTRUCTORS = FORMER_CONSTRUCTORS_SOURCE
    INDIANAPOLIS_ONLY_CONSTRUCTORS = INDIANAPOLIS_ONLY_CONSTRUCTORS_SOURCE
    TYRE_MANUFACTURERS = TYRE_MANUFACTURERS_SOURCE

    @classmethod
    def from_io(cls, value: str) -> "KeySourceName":
        return cls(value)

    def __str__(self) -> str:
        return self.value
