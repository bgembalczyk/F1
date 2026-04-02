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


@dataclass(frozen=True, slots=True)
class LinkValue:
    text: str
    url: str | None = None

    @classmethod
    def from_object(cls, value: object) -> LinkValue | None:
        record = as_record_dict(value)
        if record is None:
            return None
        text = str(record.get("text") or "").strip()
        url = record.get("url")
        return cls(text=text, url=url if isinstance(url, str) and url else None)

    def to_dict(self) -> RecordDict:
        return {"text": self.text, "url": self.url}

    def dedupe_key(self) -> str | None:
        if self.url:
            return self.url
        if self.text:
            return self.text.casefold()
        return None


@dataclass(frozen=True, slots=True)
class DriverSeriesStats:
    race_entries: object | None
    race_starts: object | None
    extras: RecordDict

    @classmethod
    def from_dict(cls, payload: RecordDict) -> DriverSeriesStats:
        race_entries = payload.get("race_entries")
        if race_entries is None:
            race_entries = payload.get("entries")
        race_starts = payload.get("race_starts")
        if race_starts is None:
            race_starts = payload.get("starts")
        extras = {
            key: value
            for key, value in payload.items()
            if key not in {"race_entries", "entries", "race_starts", "starts"}
        }
        return cls(race_entries=race_entries, race_starts=race_starts, extras=extras)

    def to_dict(self) -> RecordDict:
        payload = dict(self.extras)
        if self.race_entries is not None:
            payload["race_entries"] = self.race_entries
        if self.race_starts is not None:
            payload["race_starts"] = self.race_starts
        return payload


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

        driver = LinkValue.from_object(self.raw.get("driver"))
        if driver is None:
            return None
        return driver.url

    def extract_identity(self) -> tuple[object | None, object | None]:
        return self.raw.get("driver"), self.raw.get("nationality")

    def extract_series_stats(self) -> DriverSeriesStats:
        payload = {
            key: value
            for key, value in self.raw.items()
            if key not in {"driver", "nationality"}
        }
        return DriverSeriesStats.from_dict(payload)

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
        team_link = LinkValue.from_object(team)
        if team_link is not None:
            return team_link.dedupe_key()

        if isinstance(team, str) and team:
            return team.casefold()

        return None

    def aliases(self) -> set[str]:
        aliases: set[str] = set()
        team = self.raw.get("team")
        team_link = LinkValue.from_object(team)
        if team_link is not None:
            if team_link.url:
                aliases.add(team_link.url)
            if team_link.text:
                aliases.add(team_link.text.casefold())

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
        year = self.raw.get("year")
        if isinstance(year, int):
            return year
        return None

    def append_livery(self, livery_payload: RecordDict) -> None:
        existing_liveries = self.raw.get("liveries")
        if isinstance(existing_liveries, list):
            existing_liveries.append(livery_payload)
            return
        existing_livery = self.raw.pop("livery", None)
        season_liveries: list[object] = []
        if existing_livery is not None:
            season_liveries.append(existing_livery)
        season_liveries.append(livery_payload)
        self.raw["liveries"] = season_liveries
