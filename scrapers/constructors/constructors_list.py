from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.list.scraper import F1ListScraper
from scrapers.base.single_wiki_article.section_selection_strategy import (
    WikipediaSectionByIdSelectionStrategy,
)
from scrapers.base.source_catalog import CONSTRUCTORS_LIST
from scrapers.constructors.current_constructors_list import CurrentConstructorsListScraper
from scrapers.constructors.former_constructors_list import FormerConstructorsListScraper
from scrapers.constructors.indianapolis_only_constructors_list import (
    IndianapolisOnlyConstructorsListScraper,
)
from scrapers.constructors.privateer_teams_list import PrivateerTeamsListScraper
from scrapers.constructors.sections.list_section import CurrentConstructorsSectionParser
from scrapers.constructors.sections.list_section import FormerConstructorsSectionParser
from scrapers.constructors.indianapolis_only_constructors_list import (
    IndianapolisOnlySubSectionParser,
)
from scrapers.constructors.privateer_teams_list import PrivateerTeamsSectionParser
from scrapers.base.results import ScrapeResult

if TYPE_CHECKING:
    from collections.abc import Sequence


class ConstructorsListScraper(F1ListScraper):
    """Combined constructors list scraper for all constructors list sections."""

    url = CONSTRUCTORS_LIST.base_url
    combined_scraper_classes = (
        CurrentConstructorsListScraper,
        FormerConstructorsListScraper,
        IndianapolisOnlyConstructorsListScraper,
        PrivateerTeamsListScraper,
    )

    _SECTION_PARSER_EXPORT_KEY = "section_parser"
    _SUB_SECTION_PARSER_EXPORT_KEY = "sub_section_parser"
    _SUPPORTED_EXPORT_SCOPES = {"all", "current", "former", "indianapolis", "privateer"}

    def __init__(self, *args: Any, export_scope: str = "all", **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if export_scope not in self._SUPPORTED_EXPORT_SCOPES:
            msg = f"Unsupported export_scope='{export_scope}' for {self.__class__.__name__}"
            raise ValueError(msg)
        self._export_scope = export_scope
        self._split_export_records: dict[str, list[dict[str, Any]]] = {
            self._SECTION_PARSER_EXPORT_KEY: [],
            self._SUB_SECTION_PARSER_EXPORT_KEY: [],
        }

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        selector = WikipediaSectionByIdSelectionStrategy(domain="constructors")
        self._split_export_records = {
            self._SECTION_PARSER_EXPORT_KEY: [],
            self._SUB_SECTION_PARSER_EXPORT_KEY: [],
        }
        records: list[dict[str, Any]] = []

        current_section = selector.extract_section_by_id(
            soup,
            CurrentConstructorsListScraper.CONFIG.section_id,
            domain="constructors",
        )
        if current_section is not None:
            current_parser = CurrentConstructorsSectionParser(
                config=CurrentConstructorsListScraper.CONFIG,
                section_label=CurrentConstructorsListScraper.section_label,
                include_urls=self.include_urls,
                normalize_empty_values=self.normalize_empty_values,
            )
            current_records = current_parser.parse(current_section).records
            if self._should_include_scope("current"):
                records.extend(current_records)
            self._split_export_records[self._SECTION_PARSER_EXPORT_KEY].extend(
                current_records,
            )

        former_section = selector.extract_section_by_id(
            soup,
            FormerConstructorsListScraper.CONFIG.section_id,
            domain="constructors",
        )
        if former_section is not None:
            former_parser = FormerConstructorsSectionParser(
                config=FormerConstructorsListScraper.CONFIG,
                section_label=FormerConstructorsListScraper.section_label,
                include_urls=self.include_urls,
                normalize_empty_values=self.normalize_empty_values,
            )
            former_records = former_parser.parse(former_section).records
            if self._should_include_scope("former"):
                records.extend(former_records)
            self._split_export_records[self._SECTION_PARSER_EXPORT_KEY].extend(
                former_records,
            )
            indianapolis_records = self._parse_indianapolis_only_records(former_section)
            if self._should_include_scope("indianapolis"):
                records.extend(indianapolis_records)

        privateer_section = selector.extract_section_by_id(
            soup,
            PrivateerTeamsListScraper.section_id,
            domain="constructors",
        )
        if privateer_section is not None:
            privateer_parser = PrivateerTeamsSectionParser()
            privateer_records = privateer_parser.parse(privateer_section).get("items", [])
            if not self.include_urls:
                for record in privateer_records:
                    if isinstance(record, dict):
                        record.pop("team_url", None)
            else:
                for record in privateer_records:
                    if not isinstance(record, dict):
                        continue
                    url = record.get("team_url")
                    if isinstance(url, str) and url.startswith("/"):
                        record["team_url"] = self._full_url(url)
            if self._should_include_scope("privateer"):
                records.extend(privateer_records)
            self._split_export_records[self._SUB_SECTION_PARSER_EXPORT_KEY].extend(
                privateer_records,
            )

        return records

    def _parse_indianapolis_only_records(self, former_section: Any) -> list[dict[str, Any]]:
        parser = IndianapolisOnlySubSectionParser()
        parsed = parser.parse(former_section)
        parsed_records = parsed.get("items", [])
        if not isinstance(parsed_records, list):
            return []
        records: list[dict[str, Any]] = []
        for record in parsed_records:
            if not isinstance(record, dict):
                continue
            normalized = dict(record)
            if not self.include_urls:
                normalized.pop("constructor_url", None)
            else:
                url = normalized.get("constructor_url")
                if isinstance(url, str) and url.startswith("/"):
                    normalized["constructor_url"] = self._full_url(url)
            records.append(normalized)
        return records

    def _should_include_scope(self, scope: str) -> bool:
        return self._export_scope in {"all", scope}

    def to_json(
        self,
        path: str | Path,
        *,
        indent: int = 2,
        include_metadata: bool = False,
    ) -> None:
        super().to_json(path, indent=indent, include_metadata=include_metadata)
        self._export_split_json(path, indent=indent, include_metadata=include_metadata)

    def to_csv(
        self,
        path: str | Path,
        *,
        fieldnames: Sequence[str] | None = None,
        fieldnames_strategy: str = "union",
        include_metadata: bool = False,
    ) -> None:
        super().to_csv(
            path,
            fieldnames=fieldnames,
            fieldnames_strategy=fieldnames_strategy,
            include_metadata=include_metadata,
        )
        self._export_split_csv(
            path,
            fieldnames=fieldnames,
            fieldnames_strategy=fieldnames_strategy,
            include_metadata=include_metadata,
        )

    def _export_split_json(
        self,
        path: str | Path,
        *,
        indent: int,
        include_metadata: bool,
    ) -> None:
        for parser_kind, split_records in self._split_export_records.items():
            if not split_records:
                continue
            split_path = self._split_export_path(path, parser_kind)
            split_result = ScrapeResult(data=split_records, source_url=self.url)
            self.result_export_service.to_json(
                split_result,
                split_path,
                exporter=self.exporter,
                indent=indent,
                include_metadata=include_metadata,
            )

    def _export_split_csv(
        self,
        path: str | Path,
        *,
        fieldnames: Sequence[str] | None,
        fieldnames_strategy: str,
        include_metadata: bool,
    ) -> None:
        for parser_kind, split_records in self._split_export_records.items():
            if not split_records:
                continue
            split_path = self._split_export_path(path, parser_kind)
            split_result = ScrapeResult(data=split_records, source_url=self.url)
            self.result_export_service.to_csv(
                split_result,
                split_path,
                exporter=self.exporter,
                fieldnames=fieldnames,
                fieldnames_strategy=fieldnames_strategy,
                include_metadata=include_metadata,
            )

    @staticmethod
    def _split_export_path(path: str | Path, parser_kind: str) -> Path:
        output_path = Path(path)
        return output_path.with_name(f"{output_path.stem}_{parser_kind}{output_path.suffix}")


if __name__ == "__main__":
    from scrapers.base.deprecated_entrypoint import run_deprecated_entrypoint

    run_deprecated_entrypoint()
