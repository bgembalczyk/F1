from __future__ import annotations

from dataclasses import dataclass
from typing import TypeGuard

RecordDict = dict[str, object]

FIELD_TEXT = "text"
FIELD_URL = "url"
FIELD_DRIVER = "driver"
FIELD_DRIVER_URL = "driver_url"
FIELD_TEAM = "team"
FIELD_SEASON = "season"
FIELD_YEAR = "year"
FIELD_LIVERY = "livery"
FIELD_LIVERIES = "liveries"
FIELD_RACING_SERIES = "racing_series"
FIELD_FORMULA_ONE = "formula_one"


def is_record_dict(value: object) -> TypeGuard[RecordDict]:
    return isinstance(value, dict)


def as_record_dict(value: object) -> RecordDict | None:
    if not is_record_dict(value):
        return None
    return value


@dataclass(slots=True, frozen=True)
class LinkValue:
    text: str | None
    url: str | None

    @classmethod
    def from_object(cls, value: object) -> LinkValue | None:
        record = as_record_dict(value)
        if record is None:
            return None
        text = record.get(FIELD_TEXT)
        url = record.get(FIELD_URL)
        return cls(
            text=text if isinstance(text, str) and text else None,
            url=url if isinstance(url, str) and url else None,
        )

    def canonical_key(self) -> str | None:
        if self.url:
            return self.url
        if self.text:
            return self.text.casefold()
        return None

    def display_text(self) -> str:
        return self.text or ""


@dataclass(slots=True)
class DriverRecordModel:
    raw: RecordDict

    @classmethod
    def from_object(cls, value: object) -> DriverRecordModel | None:
        record = as_record_dict(value)
        if record is None:
            return None
        return cls(raw=record)

    def driver_link(self) -> LinkValue | None:
        return LinkValue.from_object(self.raw.get(FIELD_DRIVER))

    def dedupe_key(self) -> str | None:
        driver_url = self.raw.get(FIELD_DRIVER_URL)
        if isinstance(driver_url, str) and driver_url:
            return driver_url

        driver_link = self.driver_link()
        if driver_link is None:
            return None
        return driver_link.url

    def to_dict(self) -> RecordDict:
        return self.raw


@dataclass(slots=True)
class TeamRecordModel:
    raw: RecordDict

    @classmethod
    def from_object(cls, value: object) -> TeamRecordModel | None:
        record = as_record_dict(value)
        if record is None:
            return None
        return cls(raw=record)

    def team_link(self) -> LinkValue | None:
        return LinkValue.from_object(self.raw.get(FIELD_TEAM))

    def dedupe_key(self) -> str | None:
        team_link = self.team_link()
        if team_link is not None:
            return team_link.canonical_key()
        team_name = self.raw.get(FIELD_TEAM)
        if isinstance(team_name, str) and team_name:
            return team_name.casefold()
        return None

    def aliases(self) -> set[str]:
        aliases: set[str] = set()
        team_link = self.team_link()
        if team_link is not None:
            if team_link.url:
                aliases.add(team_link.url)
            if team_link.text:
                aliases.add(team_link.text.casefold())

        team_name = self.raw.get(FIELD_TEAM)
        if isinstance(team_name, str) and team_name:
            aliases.add(team_name.casefold())

        return aliases

    def to_dict(self) -> RecordDict:
        return self.raw


@dataclass(slots=True)
class EngineRecordModel:
    raw: RecordDict

    @classmethod
    def from_object(cls, value: object) -> EngineRecordModel | None:
        record = as_record_dict(value)
        if record is None:
            return None
        return cls(raw=record)

    def to_dict(self) -> RecordDict:
        return self.raw


@dataclass(slots=True)
class SeasonRecordModel:
    raw: RecordDict

    @classmethod
    def from_object(cls, value: object) -> SeasonRecordModel | None:
        record = as_record_dict(value)
        if record is None:
            return None
        return cls(raw=record)

    def year(self) -> int | None:
        year = self.raw.get(FIELD_YEAR)
        return year if isinstance(year, int) else None

    def append_livery(self, livery_payload: RecordDict) -> None:
        existing_liveries = self.raw.get(FIELD_LIVERIES)
        if isinstance(existing_liveries, list):
            existing_liveries.append(livery_payload)
            return

        existing_livery = self.raw.pop(FIELD_LIVERY, None)
        season_liveries: list[object] = []
        if existing_livery is not None:
            season_liveries.append(existing_livery)
        season_liveries.append(livery_payload)
        self.raw[FIELD_LIVERIES] = season_liveries

    def to_dict(self) -> RecordDict:
        return self.raw


@dataclass(slots=True)
class LiveryRecordModel:
    raw: RecordDict

    @classmethod
    def from_object(cls, value: object) -> LiveryRecordModel | None:
        record = as_record_dict(value)
        if record is None:
            return None
        return cls(raw=record)

    def season_years(self) -> set[int]:
        return _season_years_from_value(self.raw.get(FIELD_SEASON))

    def payload_without_season(self) -> RecordDict:
        return {
            key: value
            for key, value in self.raw.items()
            if key != FIELD_SEASON
        }


def _season_years_from_value(value: object) -> set[int]:
    years: set[int] = set()
    if isinstance(value, dict):
        year = value.get(FIELD_YEAR)
        if isinstance(year, int):
            years.add(year)
        return years

    if isinstance(value, list):
        for item in value:
            years.update(_season_years_from_value(item))

    return years


@dataclass(slots=True)
class RaceRecordModel:
    raw: RecordDict

    @classmethod
    def from_object(cls, value: object) -> RaceRecordModel | None:
        record = as_record_dict(value)
        if record is None:
            return None
        return cls(raw=record)

    def to_dict(self) -> RecordDict:
        return self.raw
