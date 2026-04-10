from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from models.value_objects.common_terms import EntityName
from models.value_objects.common_terms import SectionId
from scrapers.base.sections.serializer import build_section_parse_result
from scrapers.base.sections.table_section_parser import TableSectionParser
from scrapers.base.table.parser import HtmlTableParser
from scrapers.constructors import constructors_constants
from scrapers.wiki.parsers.elements.list import ListParser
from scrapers.wiki.parsers.elements.wiki_table.base import WikiTableBaseParser
from scrapers.wiki.parsers.sections.section import SectionParser as WikiSectionParser
from scrapers.wiki.parsers.sections.sub_section import SubSectionParser

if TYPE_CHECKING:
    from scrapers.base.sections.interface import SectionParseResult
    from scrapers.base.table.config import ScraperConfig

logger = logging.getLogger(__name__)


class IndianapolisConstructorsListParser(ListParser):
    def parse(self, element: Tag) -> dict[str, list[dict[str, Any]]]:
        items: list[dict[str, Any]] = []
        for li in element.find_all("li", recursive=False):
            anchor = li.find("a")
            constructor = li.get_text(" ", strip=True)
            if not constructor:
                continue
            row: dict[str, Any] = {
                "chassis_constructor": {
                    "text": constructor,
                },
            }
            if anchor and anchor.has_attr("href"):
                row["chassis_constructor"]["url"] = anchor["href"]
            items.append(row)
        return {"items": items}


class IndianapolisOnlySubSectionParser(SubSectionParser):
    def __init__(self) -> None:
        super().__init__()
        self._list_parser = IndianapolisConstructorsListParser()

    def parse(self, element: Tag, *args: Any, **kwargs: Any) -> dict[str, Any]:
        list_root = element.find(["ul", "ol"])
        if isinstance(list_root, Tag):
            return self._list_parser.parse(list_root)
        return self.parse_group(list(element.children), *args, **kwargs)

    def parse_group(
        self,
        elements: list,
        *_args: Any,
        **_kwargs: Any,
    ) -> dict[str, Any]:
        for candidate in elements:
            if isinstance(candidate, Tag) and candidate.name in {"ul", "ol"}:
                return self._list_parser.parse(candidate)
        return {"items": []}


class CurrentConstructorsTableParser(WikiTableBaseParser):
    table_type = "current_constructors"

    def matches(self, headers: list[str], table_data: dict[str, Any]) -> bool:
        del table_data
        expected = {
            constants.CONSTRUCTOR_NAME_HEADER.lower(),
            constants.CONSTRUCTOR_ENGINE_HEADER.lower(),
            constants.CONSTRUCTOR_LICENSED_IN_HEADER.lower(),
            constants.CONSTRUCTOR_BASED_IN_HEADER.lower(),
            constants.CONSTRUCTOR_SEASONS_HEADER.lower(),
            constants.CONSTRUCTOR_RACES_ENTERED_HEADER.lower(),
            constants.CONSTRUCTOR_RACES_STARTED_HEADER.lower(),
            constants.CONSTRUCTOR_TOTAL_ENTRIES_HEADER.lower(),
            constants.CONSTRUCTOR_WINS_HEADER.lower(),
            constants.CONSTRUCTOR_POINTS_HEADER.lower(),
            constants.CONSTRUCTOR_POLES_HEADER.lower(),
            constants.CONSTRUCTOR_FASTEST_LAPS_HEADER.lower(),
            constants.CONSTRUCTOR_PODIUMS_HEADER.lower(),
            constants.CONSTRUCTOR_WCC_HEADER.lower(),
            constants.CONSTRUCTOR_WDC_HEADER.lower(),
            constants.CONSTRUCTOR_ANTECEDENT_TEAMS_HEADER.lower(),
        }
        normalized = {header.strip().lower() for header in headers}
        return expected.issubset(normalized)

    _HEADER_TO_KEY: dict[str, str] = {
        constants.CONSTRUCTOR_NAME_HEADER: "constructor",
        constants.CONSTRUCTOR_ENGINE_HEADER: "engine",
        constants.CONSTRUCTOR_LICENSED_IN_HEADER: "licensed_in",
        constants.CONSTRUCTOR_BASED_IN_HEADER: "based_in",
        constants.CONSTRUCTOR_SEASONS_HEADER: "seasons",
        constants.CONSTRUCTOR_RACES_ENTERED_HEADER: "races_entered",
        constants.CONSTRUCTOR_RACES_STARTED_HEADER: "races_started",
        constants.CONSTRUCTOR_DRIVERS_HEADER: "drivers",
        constants.CONSTRUCTOR_TOTAL_ENTRIES_HEADER: "total_entries",
        constants.CONSTRUCTOR_WINS_HEADER: "wins",
        constants.CONSTRUCTOR_POINTS_HEADER: "points",
        constants.CONSTRUCTOR_POLES_HEADER: "poles",
        constants.CONSTRUCTOR_FASTEST_LAPS_HEADER: "fastest_laps",
        constants.CONSTRUCTOR_PODIUMS_HEADER: "podiums",
        constants.CONSTRUCTOR_WCC_HEADER: "wcc_titles",
        constants.CONSTRUCTOR_WDC_HEADER: "wdc_titles",
        constants.CONSTRUCTOR_ANTECEDENT_TEAMS_HEADER: "antecedent_teams",
    }

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {
            header: self._HEADER_TO_KEY.get(
                header.strip(),
                header.strip().lower().replace(" ", "_"),
            )
            for header in headers
        }


class FormerConstructorsTableParser(WikiTableBaseParser):
    table_type = "former_constructors"

    def matches(self, headers: list[str], table_data: dict[str, Any]) -> bool:
        del table_data
        expected = {
            constants.CONSTRUCTOR_NAME_HEADER.lower(),
            constants.CONSTRUCTOR_LICENSED_IN_HEADER.lower(),
            constants.CONSTRUCTOR_SEASONS_HEADER.lower(),
        }
        normalized = {header.strip().lower() for header in headers}
        return expected.issubset(normalized)

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {header: header.strip().lower().replace(" ", "_") for header in headers}


class ConstructorsSectionParser(WikiSectionParser):
    def __init__(
        self,
        *,
        config: ScraperConfig,
        section_label: str | None,
        include_urls: bool,
        normalize_empty_values: bool,
        table_parser: WikiTableBaseParser,
    ) -> None:
        super().__init__()
        self._include_urls = include_urls
        self._parser = TableSectionParser(
            config=config,
            section_id=config.section_id or "constructors",
            section_label=section_label or "Constructors",
            domain="constructors",
            include_urls=include_urls,
            normalize_empty_values=normalize_empty_values,
        )
        self._table_parser = table_parser
        self._html_table_parser = HtmlTableParser()

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        logger.warning(
            "Constructors section parser '%s': start parse.",
            self._parser.section_label,
        )
        table = section_fragment.find("table", class_="wikitable")
        logger.warning(
            "Constructors section parser '%s': first wikitable found=%s.",
            self._parser.section_label,
            table is not None,
        )
        if table is not None:
            try:
                rows = self._html_table_parser.parse_table(table)
                headers = rows[0].headers if rows else []
                logger.warning(
                    "Constructors section parser '%s': first table headers=%s.",
                    self._parser.section_label,
                    headers,
                )
                row_maps = [
                    {
                        header: cell.get_text(" ", strip=True)
                        for header, cell in zip(row.headers, row.cells, strict=False)
                    }
                    for row in rows
                ]
                self._table_parser.parse({"headers": headers, "rows": row_maps})
            except RuntimeError:
                logger.warning(
                    "Constructors section parser '%s': "
                    "lightweight table pre-parse failed.",
                    self._parser.section_label,
                )
        try:
            return self._parser.parse(section_fragment)
        except RuntimeError:
            logger.warning(
                "Constructors section parser '%s': full section parse failed, "
                "trying table-only fallback.",
                self._parser.section_label,
            )
            if table is not None:
                table_only_fragment = BeautifulSoup(str(table), "html.parser")
                try:
                    return self._parser.parse(table_only_fragment)
                except RuntimeError:
                    logger.warning(
                        "Constructors section parser '%s': table-only fallback failed.",
                        self._parser.section_label,
                    )
            logger.warning(
                "Skipping constructors section '%s': matching table not found.",
                self._parser.section_label,
            )
            return build_section_parse_result(
                section_id=self._parser.section_id,
                section_label=self._parser.section_label,
                records=[],
                parser=self.__class__.__name__,
                source="wikipedia",
                extras={"domain": "constructors", "skipped": True},
            )


class CurrentConstructorsSectionParser(ConstructorsSectionParser):
    def __init__(
        self,
        *,
        config: ScraperConfig,
        section_label: str | None = None,
        include_urls: bool,
        normalize_empty_values: bool,
    ) -> None:
        super().__init__(
            config=config,
            section_label=section_label,
            include_urls=include_urls,
            normalize_empty_values=normalize_empty_values,
            table_parser=CurrentConstructorsTableParser(),
        )

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        parsed = super().parse(section_fragment)
        sorted_records = [
            self._sort_current_constructor_record_keys(
                self._normalize_constructor_fields(record),
            )
            for record in parsed.records
        ]
        return build_section_parse_result(
            section_id=str(SectionId.from_raw(parsed.section_id)),
            section_label=EntityName.from_raw(parsed.section_label).to_export(),
            records=sorted_records,
            parser=str(parsed.metadata.get("parser", self.__class__.__name__)),
            source=str(parsed.metadata.get("source", "wikipedia")),
            extras={
                key: value
                for key, value in parsed.metadata.items()
                if key not in {"parser", "source", "heading_path"}
            },
            heading_path=tuple(parsed.metadata.get("heading_path", [])),
        )

    @staticmethod
    def _normalize_constructor_fields(record: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(record)
        if "constructor" not in normalized:
            return normalized

        chassis = CurrentConstructorsSectionParser._normalize_constructor_link(
            normalized.get("constructor"),
        )
        engine = CurrentConstructorsSectionParser._normalize_constructor_link(
            normalized.get("engine"),
        )
        if engine is None:
            engine = chassis

        normalized["constructor"] = {
            "chassis_constructor": chassis,
            "engine_constructor": engine,
        }
        normalized.pop("engine", None)
        return normalized

    @staticmethod
    def _normalize_constructor_link(value: Any) -> dict[str, Any] | None:
        if isinstance(value, list):
            if not value:
                return None
            value = value[0]
        if isinstance(value, dict):
            text = value.get("text")
            url = value.get("url")
            normalized: dict[str, Any] = {}
            if text is not None:
                normalized["text"] = text
            if url is not None:
                normalized["url"] = url
            return normalized or None
        if isinstance(value, str):
            return {"text": value}
        return None

    @staticmethod
    def _sort_current_constructor_record_keys(record: dict[str, Any]) -> dict[str, Any]:
        pinned_keys = ("constructor",)
        ordered: dict[str, Any] = {}

        for key in pinned_keys:
            if key in record:
                ordered[key] = record[key]

        remaining_keys = sorted(key for key in record if key not in pinned_keys)
        for key in remaining_keys:
            ordered[key] = record[key]

        return ordered


class FormerConstructorsSectionParser(ConstructorsSectionParser):
    def __init__(
        self,
        *,
        config: ScraperConfig,
        section_label: str | None = None,
        include_urls: bool,
        normalize_empty_values: bool,
    ) -> None:
        super().__init__(
            config=config,
            section_label=section_label,
            include_urls=include_urls,
            normalize_empty_values=normalize_empty_values,
            table_parser=FormerConstructorsTableParser(),
        )
        self._indianapolis_sub_section_parser = IndianapolisOnlySubSectionParser()

    def parse(self, section_fragment: BeautifulSoup) -> SectionParseResult:
        result = super().parse(section_fragment)
        for record in result.records:
            if not isinstance(record, dict) or "constructor" not in record:
                continue
            record["chassis_constructor"] = record.pop("constructor")
        return result

    def parse_indianapolis_only_records(
        self,
        section_fragment: BeautifulSoup,
    ) -> list[dict[str, Any]]:
        parsed = self._indianapolis_sub_section_parser.parse(section_fragment)
        records = parsed.get("items", [])
        if not isinstance(records, list):
            return []

        normalized_records: list[dict[str, Any]] = []
        for record in records:
            if not isinstance(record, dict):
                continue
            normalized_constructor = self._normalize_indianapolis_constructor(record)
            if normalized_constructor is None:
                continue
            if not self._include_urls:
                normalized_constructor.pop("url", None)
            else:
                url = normalized_constructor.get("url")
                if isinstance(url, str) and url.startswith("/"):
                    normalized_constructor["url"] = f"https://en.wikipedia.org{url}"
            normalized_records.append(
                {"chassis_constructor": normalized_constructor},
            )
        return normalized_records

    @staticmethod
    def _normalize_indianapolis_constructor(
        record: dict[str, Any],
    ) -> dict[str, Any] | None:
        constructor = record.get("chassis_constructor")
        if isinstance(constructor, dict):
            return dict(constructor)

        constructor_name = record.get("constructor")
        if not isinstance(constructor_name, str) or not constructor_name.strip():
            return None

        normalized: dict[str, Any] = {"text": constructor_name.strip()}
        constructor_url = record.get("constructor_url")
        if isinstance(constructor_url, str) and constructor_url.strip():
            normalized["url"] = constructor_url.strip()
        return normalized


__all__ = [
    "IndianapolisConstructorsListParser",
    "IndianapolisOnlySubSectionParser",
    "CurrentConstructorsTableParser",
    "FormerConstructorsTableParser",
    "ConstructorsSectionParser",
    "CurrentConstructorsSectionParser",
    "FormerConstructorsSectionParser",
]
