from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Protocol

from scrapers.base.helpers.wiki import is_wikipedia_redlink


class DetailUrlResolver(Protocol):
    def resolve(self, record: dict[str, Any]) -> str | None:
        ...


@dataclass(frozen=True)
class DriverDetailUrlResolver:
    def resolve(self, record: dict[str, Any]) -> str | None:
        driver_link = record.get("driver")
        if isinstance(driver_link, dict):
            url = driver_link.get("url")
            if isinstance(url, str) and url:
                return url
        return None


@dataclass(frozen=True)
class ConstructorDetailUrlResolver:
    def resolve(self, record: dict[str, Any]) -> str | None:
        constructor = record.get("constructor")
        if isinstance(constructor, dict):
            url = constructor.get("url")
            if self._is_valid_wiki_url(url):
                return url

        constructor_url = record.get("constructor_url")
        if self._is_valid_wiki_url(constructor_url):
            return constructor_url

        team_url = record.get("team_url")
        if self._is_valid_wiki_url(team_url):
            return team_url

        return None

    @staticmethod
    def _is_valid_wiki_url(url: Any) -> bool:
        return isinstance(url, str) and bool(url) and not is_wikipedia_redlink(url)


@dataclass(frozen=True)
class CircuitDetailUrlResolver:
    def resolve(self, record: dict[str, Any]) -> str | None:
        circuit_data = record.get("circuit")
        if isinstance(circuit_data, dict):
            url = circuit_data.get("url")
            if isinstance(url, str) and url:
                return url
        return None


@dataclass(frozen=True)
class SeasonDetailUrlResolver:
    def resolve(self, record: dict[str, Any]) -> str | None:
        season_info = record.get("season")
        if isinstance(season_info, dict):
            url = season_info.get("url")
            if isinstance(url, str) and url:
                return url
        return None


@dataclass(frozen=True)
class GrandPrixDetailUrlResolver:
    def resolve(self, record: dict[str, Any]) -> str | None:
        race_title = record.get("race_title")
        if isinstance(race_title, dict):
            url = race_title.get("url")
            if isinstance(url, str) and url:
                return url
        return None


@dataclass(frozen=True)
class LegacyDetailUrlResolver:
    extractor: Any

    def resolve(self, record: dict[str, Any]) -> str | None:
        return self.extractor.get_detail_url(record)
