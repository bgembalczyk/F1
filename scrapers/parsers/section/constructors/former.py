from scrapers.configs.public import TableConfig
from scrapers.parsers.section.constructors.base import ConstructorsSectionParser
from scrapers.parsers.table.constructor.former import FormerConstructorsTableMapper
from scrapers.parsers.wiki.sublevels.indianapolis_only_sub_section import GenericIndianapolisOnlySubSectionParser
from scrapers.parsers.wiki.table.table import WikiTableHtmlParser


class FormerConstructorsSectionParser(ConstructorsSectionParser):
    def __init__(
        self,
        *,
        config: TableConfig,
        section_label: str | None = None,
        include_urls: bool,
        normalize_empty_values: bool,
    ) -> None:
        super().__init__(
            config=config,
            section_label=section_label,
            include_urls=include_urls,
            normalize_empty_values=normalize_empty_values,
            table_html_parser=WikiTableHtmlParser(),
            table_domain_mapper=FormerConstructorsTableMapper(),
        )
        self._indianapolis_sub_section_parser = GenericIndianapolisOnlySubSectionParser()

    def parse_indianapolis_only_records(
        self,
        section_fragment,
    ) -> list[dict[str, dict[str, str]]]:
        parsed = self._indianapolis_sub_section_parser.parse(section_fragment)
        records = parsed.get("items", [])
        if not isinstance(records, list):
            return []

        normalized_records: list[dict[str, dict[str, str]]] = []
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
        record: dict[str, object],
    ) -> dict[str, str] | None:
        constructor = record.get("chassis_constructor")
        if isinstance(constructor, dict):
            return {
                key: value
                for key, value in constructor.items()
                if isinstance(key, str) and isinstance(value, str)
            }

        constructor_name = record.get("constructor")
        if not isinstance(constructor_name, str) or not constructor_name.strip():
            return None

        normalized: dict[str, str] = {"text": constructor_name.strip()}
        constructor_url = record.get("constructor_url")
        if isinstance(constructor_url, str) and constructor_url.strip():
            normalized["url"] = constructor_url.strip()
        return normalized
