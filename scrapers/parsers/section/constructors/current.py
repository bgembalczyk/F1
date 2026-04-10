from typing import Any

from bs4 import BeautifulSoup

from models.entity_name import EntityName
from models.section_id import SectionId
from scrapers.config import ScraperConfig
from scrapers.parsers.section.constructors.base import ConstructorsSectionParser
from scrapers.parsers.table.current_constructors import CurrentConstructorsTableParser
from scrapers.section.parse_results import SectionParseResult
from scrapers.section.serializer import build_section_parse_result


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
