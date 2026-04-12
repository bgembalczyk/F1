from typing import Any

from scrapers.parsers.base_red_flagged_races_table_mapper import BaseRedFlaggedRacesTableMapper
from scrapers.parsers.red_flagged_helpers import RESTART_STATUS_MAP
from scrapers.parsers.red_flagged_helpers import extract_rich_cell
from scrapers.parsers.red_flagged_helpers import map_drivers_cell
from scrapers.parsers.red_flagged_helpers import map_winner_cell
from scrapers.parsers.red_flagged_helpers import try_int


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

