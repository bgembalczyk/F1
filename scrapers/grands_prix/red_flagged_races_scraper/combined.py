from __future__ import annotations

import json
from typing import TYPE_CHECKING
from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.helpers.text import strip_marks
from scrapers.base.helpers.transformers import append_transformer
from scrapers.base.source_catalog import RED_FLAGGED_RACES
from scrapers.base.transformers.failed_to_make_restart import (
    FailedToMakeRestartTransformer,
)
from scrapers.wiki.parsers.body_content import BodyContentParser
from scrapers.wiki.parsers.elements.wiki_table.base import WikiTableBaseParser
from scrapers.wiki.parsers.sections.section import SectionParser
from scrapers.wiki.parsers.sections.sub_section import SubSectionParser
from scrapers.wiki.parsers.sections.sub_sub_sub_section import SubSubSubSectionParser
from scrapers.wiki.scraper import WikiScraper

if TYPE_CHECKING:
    from scrapers.base.options import ScraperOptions

_WIKIPEDIA_BASE_URL = "https://en.wikipedia.org"
_RESTART_STATUS_MAP = {
    "N": "race_was_not_restarted",
    "Y": "race_was_restarted_over_original_distance",
    "R": "race_was_resumed_to_complete_original_distance",
    "S": "race_was_restarted_or_resumed_without_completing_original_distance",
}


def _build_full_url(url: str | None) -> str | None:
    if url is None:
        return None
    if isinstance(url, str) and url.startswith("/"):
        return _WIKIPEDIA_BASE_URL + url
    return url


def _try_int(text: str) -> int | str:
    try:
        return int(text)
    except ValueError:
        return text


def _extract_rich_cell(
    cell_data: Any,
) -> tuple[str, list[Any], str | None, str | None]:
    if isinstance(cell_data, dict) and "text" in cell_data:
        text = cell_data.get("text") or ""
        links = cell_data.get("links") or []
        background = cell_data.get("background")
        url = _build_full_url(links[0].get("url") if links else None)
        return text, links, background, url
    text = str(cell_data) if cell_data else ""
    return text, [], None, None


def _map_winner_cell(text: str, links: list[Any]) -> dict[str, Any]:
    winner_link = links[-1] if links else None
    if winner_link:
        winner_text = strip_marks(winner_link.get("text") or "") or text
        return {"text": winner_text, "url": _build_full_url(winner_link.get("url"))}
    return {"text": strip_marks(text) if text else text, "url": None}


def _map_drivers_cell(text: str, links: list[Any]) -> list[dict[str, Any]]:
    if links:
        return [
            {
                "text": strip_marks(lnk.get("text") or ""),
                "url": _build_full_url(lnk.get("url")),
            }
            for lnk in links
            if lnk.get("text")
        ]
    if text:
        return [{"text": strip_marks(text), "url": None}]
    return []


class WorldChampionshipsRacesTableParser(WikiTableBaseParser):
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

    def parse(self, table_data: dict[str, Any]) -> dict[str, Any] | None:
        result = super().parse(table_data)
        if result is None:
            return None
        result["domain_rows"] = self._merge_failed_to_restart_rows(
            result["domain_rows"],
        )
        return result

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
        _key = WorldChampionshipsRacesTableParser._race_key
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

    @staticmethod
    def _normalized_rows(table_data: dict[str, Any]) -> list[dict[str, Any]]:
        rich_rows = table_data.get("rich_rows", [])
        if isinstance(rich_rows, list) and rich_rows:
            return [row for row in rich_rows if isinstance(row, dict)]
        rows = table_data.get("rows", [])
        if isinstance(rows, list):
            dict_rows = [row for row in rows if isinstance(row, dict)]
            if dict_rows:
                return dict_rows
        raw_rows = table_data.get("raw_rows", [])
        if isinstance(raw_rows, list):
            return [row for row in raw_rows if isinstance(row, dict)]
        return []

    @staticmethod
    def _map_row(row: dict[str, Any], column_map: dict[str, str]) -> dict[str, Any]:
        mapped: dict[str, Any] = {}
        for header, cell_data in row.items():
            key = column_map.get(header)
            if not key:
                continue
            text, links, background, url = _extract_rich_cell(cell_data)
            if key in ("season", "lap"):
                mapped[key] = _try_int(text)
            elif key == "grand_prix":
                mapped[key] = {"text": text, "url": url}
            elif key == "restart_status":
                code = text[0].upper() if text else ""
                mapped[key] = {
                    "code": code,
                    "description": _RESTART_STATUS_MAP.get(code),
                }
                if background:
                    mapped["background"] = background
            elif key == "winner":
                mapped[key] = _map_winner_cell(text, links)
            elif key == "failed_to_make_restart_drivers":
                mapped[key] = _map_drivers_cell(text, links)
            else:
                mapped[key] = text
        return mapped


class NonChampionshipsRacesTableParser(WikiTableBaseParser):
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

    def parse(self, table_data: dict[str, Any]) -> dict[str, Any] | None:
        result = super().parse(table_data)
        if result is None:
            return None
        result["domain_rows"] = self._merge_failed_to_restart_rows(
            result["domain_rows"],
        )
        return result

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
        _key = NonChampionshipsRacesTableParser._race_key
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

    @staticmethod
    def _normalized_rows(table_data: dict[str, Any]) -> list[dict[str, Any]]:
        rich_rows = table_data.get("rich_rows", [])
        if isinstance(rich_rows, list) and rich_rows:
            return [row for row in rich_rows if isinstance(row, dict)]
        rows = table_data.get("rows", [])
        if isinstance(rows, list):
            dict_rows = [row for row in rows if isinstance(row, dict)]
            if dict_rows:
                return dict_rows
        raw_rows = table_data.get("raw_rows", [])
        if isinstance(raw_rows, list):
            return [row for row in raw_rows if isinstance(row, dict)]
        return []

    @staticmethod
    def _map_row(row: dict[str, Any], column_map: dict[str, str]) -> dict[str, Any]:
        mapped: dict[str, Any] = {}
        for header, cell_data in row.items():
            key = column_map.get(header)
            if not key:
                continue
            text, links, _background, url = _extract_rich_cell(cell_data)
            if key in ("season", "lap"):
                mapped[key] = _try_int(text)
            elif key == "event":
                mapped[key] = {"text": text, "url": url}
            elif key == "restart_status":
                code = text[0].upper() if text else ""
                mapped[key] = {
                    "code": code,
                    "description": _RESTART_STATUS_MAP.get(code),
                }
            elif key == "winner":
                mapped[key] = _map_winner_cell(text, links)
            elif key == "failed_to_make_restart_drivers":
                mapped[key] = _map_drivers_cell(text, links)
            else:
                mapped[key] = text
        return mapped


class NonChampionshipsRacesSubSectionParser(SubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._table_parser = NonChampionshipsRacesTableParser()
        self._fallback_element_parser = SubSubSubSectionParser()

    def parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super().parse_group(elements, context=context)
        if not self._contains_table_elements(parsed):
            parsed["elements"] = self._fallback_element_parser.parse_group(
                elements,
                context=context,
            ).get("elements", [])
        parsed.setdefault("elements", [])
        self._merge_unique_table_elements(
            parsed["elements"],
            self._extract_descendant_table_elements(elements),
        )
        self._apply_non_championship_table_parser(parsed)
        return parsed

    def _contains_table_elements(self, payload: dict[str, Any]) -> bool:
        def visit(node: Any) -> bool:
            if isinstance(node, dict):
                if node.get("kind") == "table":
                    return True
                return any(visit(value) for value in node.values())
            if isinstance(node, list):
                return any(visit(item) for item in node)
            return False

        return visit(payload)

    def _extract_descendant_table_elements(
        self,
        elements: list,
    ) -> list[dict[str, Any]]:
        table_elements: list[dict[str, Any]] = []
        seen_table_ids: set[int] = set()
        for element in elements:
            if not isinstance(element, Tag):
                continue
            for table in element.find_all("table"):
                if id(table) in seen_table_ids:
                    continue
                seen_table_ids.add(id(table))
                parsed = self._fallback_element_parser.parse_group([table]).get(
                    "elements",
                    [],
                )
                table_elements.extend(
                    parsed_element
                    for parsed_element in parsed
                    if isinstance(parsed_element, dict)
                    and parsed_element.get("kind") == "table"
                )
        return table_elements

    def _merge_unique_table_elements(
        self,
        target: list[dict[str, Any]],
        additions: list[dict[str, Any]],
    ) -> None:
        existing_signatures = {
            self._table_signature(item)
            for item in target
            if item.get("kind") == "table"
        }
        for item in additions:
            signature = self._table_signature(item)
            if signature in existing_signatures:
                continue
            existing_signatures.add(signature)
            target.append(item)

    def _table_signature(self, element: dict[str, Any]) -> tuple[Any, ...]:
        data = element.get("data")
        if not isinstance(data, dict):
            return ("invalid",)
        headers = tuple(data.get("headers", []))
        rows = data.get("rows", [])
        rows_count = len(rows) if isinstance(rows, list) else -1
        return headers, rows_count

    def _apply_non_championship_table_parser(self, payload: dict[str, Any]) -> None:
        self._apply_for_elements(payload.get("elements", []))
        for value in payload.values():
            if isinstance(value, dict):
                self._apply_non_championship_table_parser(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._apply_non_championship_table_parser(item)

    def _apply_for_elements(self, elements: list[dict[str, Any]]) -> None:
        for element in elements:
            if element.get("kind") != "table":
                continue
            data = element.get("data")
            if not isinstance(data, dict):
                continue
            parsed = self._table_parser.parse(data)
            if parsed is not None:
                element["data"] = parsed


class RedFlaggedRacesSectionParser(SectionParser):
    def __init__(self) -> None:
        super().__init__()
        self.child_parser = NonChampionshipsRacesSubSectionParser()
        self._world_championship_table_parser = WorldChampionshipsRacesTableParser()

    def parse_group(self, elements: list, *, context=None) -> dict[str, Any]:
        parsed = super().parse_group(elements, context=context)
        self._apply_world_championship_table_parser(parsed)
        return parsed

    def _apply_world_championship_table_parser(self, payload: dict[str, Any]) -> None:
        self._apply_for_elements(payload.get("elements", []))
        for value in payload.values():
            if isinstance(value, dict):
                self._apply_world_championship_table_parser(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._apply_world_championship_table_parser(item)

    def _apply_for_elements(self, elements: list[dict[str, Any]]) -> None:
        for element in elements:
            if element.get("kind") != "table":
                continue
            data = element.get("data")
            if not isinstance(data, dict):
                continue
            parsed = self._world_championship_table_parser.parse(data)
            if parsed is not None:
                element["data"] = parsed

    @staticmethod
    def collect_rows(
        payload: dict[str, Any],
        *,
        table_type: str,
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []

        def visit(node: Any) -> None:
            if isinstance(node, dict):
                if node.get("table_type") == table_type:
                    table_rows = node.get("domain_rows", [])
                    if isinstance(table_rows, list):
                        rows.extend(
                            [row for row in table_rows if isinstance(row, dict)],
                        )
                for value in node.values():
                    visit(value)
            elif isinstance(node, list):
                for item in node:
                    visit(item)

        visit(payload)
        deduplicated: list[dict[str, Any]] = []
        seen: set[str] = set()
        for row in rows:
            signature = json.dumps(row, sort_keys=True, ensure_ascii=False)
            if signature in seen:
                continue
            seen.add(signature)
            deduplicated.append(row)
        return deduplicated


class RedFlaggedRacesScraper(WikiScraper):
    """Composite scraper returning world and non-championship red-flagged races."""

    _SUPPORTED_EXPORT_SCOPES = {"all", "world_championship", "non_championship"}
    url = RED_FLAGGED_RACES.base_url

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        export_scope: str = "all",
    ) -> None:
        if export_scope not in self._SUPPORTED_EXPORT_SCOPES:
            msg = (
                f"Unsupported export_scope='{export_scope}' for "
                f"{self.__class__.__name__}"
            )
            raise ValueError(msg)
        super().__init__(
            options=append_transformer(options, FailedToMakeRestartTransformer()),
        )
        self._export_scope = export_scope
        parser = RedFlaggedRacesSectionParser()
        self.section_parser = parser
        self.body_content_parser.content_text_parser.section_parser = parser

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        body_content = BodyContentParser.find_body_content(soup)
        parsed = self.body_content_parser.parse(body_content) if body_content else {}
        world_records = RedFlaggedRacesSectionParser.collect_rows(
            parsed,
            table_type="red_flagged_world_championship_races",
        )
        non_championship_records = RedFlaggedRacesSectionParser.collect_rows(
            parsed,
            table_type="red_flagged_non_championship_races",
        )
        if self._export_scope == "world_championship":
            return world_records
        if self._export_scope == "non_championship":
            return non_championship_records
        return [*world_records, *non_championship_records]
