from __future__ import annotations

from dataclasses import dataclass
from typing import TypeGuard

RecordDict = dict[str, object]


def is_record_dict(value: object) -> TypeGuard[RecordDict]:
    return isinstance(value, dict)


def as_record_dict(value: object) -> RecordDict | None:
    if not is_record_dict(value):
        return None
    return value


@dataclass(slots=True)
class DriverRecordModel:
    raw: RecordDict

    @classmethod
    def from_object(cls, value: object) -> DriverRecordModel | None:
        record = as_record_dict(value)
        if record is None:
            return None
        return cls(raw=record)

    def dedupe_key(self) -> str | None:
        driver_url = self.raw.get("driver_url")
        if isinstance(driver_url, str) and driver_url:
            return driver_url

        driver = as_record_dict(self.raw.get("driver"))
        if driver is None:
            return None

        url = driver.get("url")
        if isinstance(url, str) and url:
            return url

        return None

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

    def dedupe_key(self) -> str | None:
        team = self.raw.get("team")
        team_link = as_record_dict(team)
        if team_link is not None:
            url = team_link.get("url")
            if isinstance(url, str) and url:
                return url
            text = team_link.get("text")
            if isinstance(text, str) and text:
                return text.casefold()

        if isinstance(team, str) and team:
            return team.casefold()

        return None

    def aliases(self) -> set[str]:
        aliases: set[str] = set()
        team = self.raw.get("team")
        team_link = as_record_dict(team)

        if team_link is not None:
            url = team_link.get("url")
            if isinstance(url, str) and url:
                aliases.add(url)
            text = team_link.get("text")
            if isinstance(text, str) and text:
                aliases.add(text.casefold())

        if isinstance(team, str) and team:
            aliases.add(team.casefold())

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
