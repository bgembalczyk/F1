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
from scrapers.constructors.config_factory import build_constructor_list_config
from scrapers.constructors.constants import CURRENT_CONSTRUCTORS_EXPECTED_HEADERS
from scrapers.constructors.constants import FORMER_CONSTRUCTORS_EXPECTED_HEADERS
from scrapers.constructors.sections.list_section import CurrentConstructorsSectionParser
from scrapers.constructors.sections.list_section import FormerConstructorsSectionParser
from scrapers.constructors.privateer_teams_list import PrivateerTeamsSectionParser
from scrapers.base.results import ScrapeResult

if TYPE_CHECKING:
    from collections.abc import Sequence


class ConstructorsListScraper(F1ListScraper):
    """Combined constructors list scraper for all constructors list sections."""

    url = CONSTRUCTORS_LIST.base_url
    _CURRENT_SECTION_ID = "Constructors_for_the_2026_season"
    _CURRENT_SECTION_FALLBACK_IDS = (
        _CURRENT_SECTION_ID,
        "Constructors_for_the_current_season",
    )
    _CURRENT_SECTION_LABEL = "Current constructors"
    _FORMER_SECTION_ID = "Former_constructors"
    _FORMER_SECTION_LABEL = "Former constructors"
    _PRIVATEER_SECTION_ID = "Privateer_teams"
    _CURRENT_CONFIG = build_constructor_list_config(
        section_id=_CURRENT_SECTION_ID,
        expected_headers=CURRENT_CONSTRUCTORS_EXPECTED_HEADERS,
        columns=[],
    )
    _FORMER_CONFIG = build_constructor_list_config(
        section_id=_FORMER_SECTION_ID,
        expected_headers=FORMER_CONSTRUCTORS_EXPECTED_HEADERS,
        columns=[],
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

        current_section = self._extract_current_section(
            selector=selector,
            soup=soup,
        )
        if current_section is not None:
            current_parser = CurrentConstructorsSectionParser(
                config=self._CURRENT_CONFIG,
                section_label=self._CURRENT_SECTION_LABEL,
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
            self._FORMER_SECTION_ID,
            domain="constructors",
        )
        if former_section is not None:
            former_parser = FormerConstructorsSectionParser(
                config=self._FORMER_CONFIG,
                section_label=self._FORMER_SECTION_LABEL,
                include_urls=self.include_urls,
                normalize_empty_values=self.normalize_empty_values,
            )
            former_records = former_parser.parse(former_section).records
            if self._should_include_scope("former"):
                records.extend(former_records)
            self._split_export_records[self._SECTION_PARSER_EXPORT_KEY].extend(
                former_records,
            )
            indianapolis_records = former_parser.parse_indianapolis_only_records(
                former_section,
            )
            if self._should_include_scope("indianapolis"):
                records.extend(indianapolis_records)

        privateer_section = selector.extract_section_by_id(
            soup,
            self._PRIVATEER_SECTION_ID,
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

    def _extract_current_section(
        self,
        *,
        selector: WikipediaSectionByIdSelectionStrategy,
        soup: BeautifulSoup,
    ) -> BeautifulSoup | None:
        for section_id in self._CURRENT_SECTION_FALLBACK_IDS:
            section = selector.extract_section_by_id(
                soup,
                section_id,
                domain="constructors",
            )
            if section is not None:
                return section
        return None

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
