from __future__ import annotations

from typing import Any

from scrapers.helpers.text import strip_marks
from scrapers.parsers.wiki.table.base import WikiTableBaseMapper

WIKIPEDIA_BASE_URL = "https://en.wikipedia.org"
RESTART_STATUS_MAP = {
    "N": "race_was_not_restarted",
    "Y": "race_was_restarted_over_original_distance",
    "R": "race_was_resumed_to_complete_original_distance",
    "S": "race_was_restarted_or_resumed_without_completing_original_distance",
}


def build_full_url(url: str | None) -> str | None:
    if url is None:
        return None
    if isinstance(url, str) and url.startswith("/"):
        return WIKIPEDIA_BASE_URL + url
    return url


def try_int(text: str) -> int | str:
    try:
        return int(text)
    except ValueError:
        return text


def extract_rich_cell(
    cell_data: Any,
) -> tuple[str, list[Any], str | None, str | None]:
    if isinstance(cell_data, dict) and "text" in cell_data:
        text = cell_data.get("text") or ""
        links = cell_data.get("links") or []
        background = cell_data.get("background")
        url = build_full_url(links[0].get("url") if links else None)
        return text, links, background, url
    text = str(cell_data) if cell_data else ""
    return text, [], None, None


def map_winner_cell(text: str, links: list[Any]) -> dict[str, Any]:
    winner_link = links[-1] if links else None
    if winner_link:
        winner_text = strip_marks(winner_link.get("text") or "") or text
        return {"text": winner_text, "url": build_full_url(winner_link.get("url"))}
    return {"text": strip_marks(text) if text else text, "url": None}


def map_drivers_cell(text: str, links: list[Any]) -> list[dict[str, Any]]:
    if links:
        return [
            {
                "text": strip_marks(lnk.get("text") or ""),
                "url": build_full_url(lnk.get("url")),
            }
            for lnk in links
            if lnk.get("text")
        ]
    if text:
        return [{"text": strip_marks(text), "url": None}]
    return []


class BaseRedFlaggedRacesTableMapper(WikiTableBaseMapper):
    def map(self, table_data: dict[str, Any]) -> dict[str, Any] | None:
        result = super().map(table_data)
        if result is None:
            return None
        result["domain_rows"] = self._merge_failed_to_restart_rows(
            result["domain_rows"],
        )
        return result

    @staticmethod
    def _race_key(row: dict[str, Any]) -> tuple:
        raise NotImplementedError

    @classmethod
    def _merge_failed_to_restart_rows(
        cls,
        rows: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        merged: list[dict[str, Any]] = []
        for row in rows:
            raw_drivers = row.pop("failed_to_make_restart_drivers", None)
            drivers = raw_drivers if raw_drivers is not None else []
            reason = row.pop("failed_to_make_restart_reason", None)
            race_key = cls._race_key(row)
            has_data = bool(drivers or reason)
            entry = {"drivers": drivers, "reason": reason} if has_data else None
            if merged and cls._race_key(merged[-1]) == race_key:
                if entry is not None:
                    merged[-1]["failed_to_make_restart"].append(entry)
            else:
                row["failed_to_make_restart"] = [entry] if entry is not None else []
                merged.append(row)
        return merged


class WorldChampionshipsRacesTableMapper(BaseRedFlaggedRacesTableMapper):
    table_type = "red_flagged_world_championship_races"
    missing_columns_policy = "ignore"
    extra_columns_policy = "ignore"

    _column_mapping = {
        "Year": "season",
        "Grand Prix": "grand_prix",
        "Lap": "lap",
        "R": "restart_status",
        "Winner": "winner",
        "Incident that prompted red flag": "incident",
        "Drivers": "failed_to_make_restart_drivers",
        "Reason": "failed_to_make_restart_reason",
    }

    def matches(self, headers: list[str], _table_data: dict[str, Any]) -> bool:
        required_headers = {
            "Year",
            "Grand Prix",
            "Lap",
            "R",
            "Winner",
            "Incident that prompted red flag",
        }
        return required_headers.issubset(set(headers))

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {
            header: self._column_mapping[header]
            for header in headers
            if header in self._column_mapping
        }

    @staticmethod
    def _race_key(row: dict[str, Any]) -> tuple:
        season = row.get("season")
        gp = row.get("grand_prix")
        gp_text = gp.get("text") if isinstance(gp, dict) else gp
        lap = row.get("lap")
        return (season, gp_text, lap)

    @staticmethod
    def _merge_failed_to_restart_rows(
        rows: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        _key = WorldChampionshipsRacesTableMapper._race_key
        merged: list[dict[str, Any]] = []
        for row in rows:
            raw_drivers = row.pop("failed_to_make_restart_drivers", None)
            drivers = raw_drivers if raw_drivers is not None else []
            reason = row.pop("failed_to_make_restart_reason", None)
            race_key = _key(row)
            has_data = bool(drivers or reason)
            entry = {"drivers": drivers, "reason": reason} if has_data else None
            if merged and _key(merged[-1]) == race_key:
                if entry is not None:
                    merged[-1]["failed_to_make_restart"].append(entry)
            else:
                row["failed_to_make_restart"] = [entry] if entry is not None else []
                merged.append(row)
        return merged

    def parse_row(self, row: dict[str, Any], column_map: dict[str, str]) -> dict[str, Any]:
        mapped: dict[str, Any] = {}
        for header, cell_data in row.items():
            key = column_map.get(header)
            if not key:
                continue
            text, links, background, url = extract_rich_cell(cell_data)
            if key in ("season", "lap"):
                mapped[key] = try_int(text)
            elif key == "grand_prix":
                mapped[key] = {"text": text, "url": url}
            elif key == "restart_status":
                code = text[0].upper() if text else ""
                mapped[key] = {
                    "code": code,
                    "description": RESTART_STATUS_MAP.get(code),
                }
                if background:
                    mapped["background"] = background
            elif key == "winner":
                mapped[key] = map_winner_cell(text, links)
            elif key == "failed_to_make_restart_drivers":
                mapped[key] = map_drivers_cell(text, links)
            else:
                mapped[key] = text
        return mapped


class NonChampionshipsRacesTableMapper(BaseRedFlaggedRacesTableMapper):
    table_type = "red_flagged_non_championship_races"
    missing_columns_policy = "ignore"
    extra_columns_policy = "ignore"

    _column_mapping = {
        "Year": "season",
        "Event": "event",
        "Lap": "lap",
        "R": "restart_status",
        "Winner": "winner",
        "Incident that prompted red flag": "incident",
        "Failed to make the restart - Drivers": "failed_to_make_restart_drivers",
        "Failed to make the restart - Reason": "failed_to_make_restart_reason",
    }

    def matches(self, headers: list[str], _table_data: dict[str, Any]) -> bool:
        required_headers = {
            "Year",
            "Event",
            "Lap",
            "R",
            "Winner",
            "Incident that prompted red flag",
        }
        return required_headers.issubset(set(headers))

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {
            header: self._column_mapping[header]
            for header in headers
            if header in self._column_mapping
        }

    @staticmethod
    def _race_key(row: dict[str, Any]) -> tuple:
        season = row.get("season")
        event = row.get("event")
        event_text = event.get("text") if isinstance(event, dict) else event
        lap = row.get("lap")
        return (season, event_text, lap)

    @staticmethod
    def _merge_failed_to_restart_rows(
        rows: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        _key = NonChampionshipsRacesTableMapper._race_key
        merged: list[dict[str, Any]] = []
        for row in rows:
            raw_drivers = row.pop("failed_to_make_restart_drivers", None)
            drivers = raw_drivers if raw_drivers is not None else []
            reason = row.pop("failed_to_make_restart_reason", None)
            race_key = _key(row)
            has_data = bool(drivers or reason)
            entry = {"drivers": drivers, "reason": reason} if has_data else None
            if merged and _key(merged[-1]) == race_key:
                if entry is not None:
                    merged[-1]["failed_to_make_restart"].append(entry)
            else:
                row["failed_to_make_restart"] = [entry] if entry is not None else []
                merged.append(row)
        return merged

    def parse_row(self, row: dict[str, Any], column_map: dict[str, str]) -> dict[str, Any]:
        mapped: dict[str, Any] = {}
        for header, cell_data in row.items():
            key = column_map.get(header)
            if not key:
                continue
            text, links, _background, url = extract_rich_cell(cell_data)
            if key in ("season", "lap"):
                mapped[key] = try_int(text)
            elif key == "event":
                mapped[key] = {"text": text, "url": url}
            elif key == "restart_status":
                code = text[0].upper() if text else ""
                mapped[key] = {
                    "code": code,
                    "description": RESTART_STATUS_MAP.get(code),
                }
            elif key == "winner":
                mapped[key] = map_winner_cell(text, links)
            elif key == "failed_to_make_restart_drivers":
                mapped[key] = map_drivers_cell(text, links)
            else:
                mapped[key] = text
        return mapped
