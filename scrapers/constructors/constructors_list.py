from __future__ import annotations

import logging
from copy import deepcopy
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.list.scraper import F1ListScraper
from scrapers.base.results import ScrapeResult
from scrapers.base.single_wiki_article.section_selection_strategy import (
    WikipediaSectionByIdSelectionStrategy,
)
from scrapers.base.source_catalog import CONSTRUCTORS_LIST
from scrapers.base.table.builders import MetricColumnSpec
from scrapers.base.table.builders import build_metric_columns
from scrapers.base.table.columns.types import AutoColumn
from scrapers.base.table.columns.types import LinksListColumn
from scrapers.base.table.dsl.column import ColumnSpec
from scrapers.constructors.base_constructor_list_scraper import (
    BaseConstructorListScraper,
)
from scrapers.constructors.config_factory import build_constructor_list_config
from scrapers.constructors.constants import CONSTRUCTOR_ANTECEDENT_TEAMS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_BASED_IN_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_DRIVERS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_ENGINE_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_FASTEST_LAPS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_LICENSED_IN_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_PODIUMS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_POINTS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_POLES_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_RACES_ENTERED_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_RACES_STARTED_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_SEASONS_HEADER
from scrapers.constructors.constants import CONSTRUCTOR_WINS_HEADER
from scrapers.constructors.constants import CURRENT_CONSTRUCTORS_EXPECTED_HEADERS
from scrapers.constructors.constants import FORMER_CONSTRUCTORS_EXPECTED_HEADERS
from scrapers.constructors.privateer_teams_list import PrivateerTeamsSectionParser
from scrapers.constructors.sections.list_section import CurrentConstructorsSectionParser
from scrapers.constructors.sections.list_section import FormerConstructorsSectionParser

if TYPE_CHECKING:
    from collections.abc import Sequence

    from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


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
    _CURRENT_SCHEMA_COLUMNS = BaseConstructorListScraper.build_schema_columns(
        [ColumnSpec(CONSTRUCTOR_ENGINE_HEADER, "engine", LinksListColumn())],
        [ColumnSpec(CONSTRUCTOR_LICENSED_IN_HEADER, "licensed_in", AutoColumn())],
        [ColumnSpec(CONSTRUCTOR_BASED_IN_HEADER, "based_in", LinksListColumn())],
        BaseConstructorListScraper.build_common_stats_columns(),
        [ColumnSpec(CONSTRUCTOR_DRIVERS_HEADER, "drivers", AutoColumn())],
        BaseConstructorListScraper.build_common_metadata_columns(),
        [
            ColumnSpec(
                CONSTRUCTOR_ANTECEDENT_TEAMS_HEADER,
                "antecedent_teams",
                LinksListColumn(),
            ),
        ],
    )
    _CURRENT_CONFIG = build_constructor_list_config(
        section_id=_CURRENT_SECTION_ID,
        expected_headers=CURRENT_CONSTRUCTORS_EXPECTED_HEADERS,
        columns=_CURRENT_SCHEMA_COLUMNS,
    )
    _FORMER_CONFIG = build_constructor_list_config(
        section_id=_FORMER_SECTION_ID,
        expected_headers=FORMER_CONSTRUCTORS_EXPECTED_HEADERS,
        columns=BaseConstructorListScraper.build_schema_columns(
            BaseConstructorListScraper.build_common_metadata_columns(),
            [BaseConstructorListScraper.build_licensed_in_ColumnSpec()],
            build_metric_columns(
                [
                    MetricColumnSpec(CONSTRUCTOR_SEASONS_HEADER, "seasons", "seasons"),
                    MetricColumnSpec(
                        CONSTRUCTOR_RACES_ENTERED_HEADER,
                        "races_entered",
                        "races_entered",
                    ),
                    MetricColumnSpec(
                        CONSTRUCTOR_RACES_STARTED_HEADER,
                        "races_started",
                        "races_started",
                    ),
                    MetricColumnSpec(CONSTRUCTOR_WINS_HEADER, "wins", "wins"),
                    MetricColumnSpec(CONSTRUCTOR_POINTS_HEADER, "points", "points"),
                    MetricColumnSpec(CONSTRUCTOR_POLES_HEADER, "poles", "poles"),
                    MetricColumnSpec(
                        CONSTRUCTOR_FASTEST_LAPS_HEADER,
                        "fastest_laps",
                        "fastest_laps",
                    ),
                    MetricColumnSpec(CONSTRUCTOR_PODIUMS_HEADER, "podiums", "podiums"),
                ],
            ),
        ),
    )

    _CURRENT_SECTION_PARSER_EXPORT_KEY = "current_constructors"
    _FORMER_SECTION_PARSER_EXPORT_KEY = "former_constructors"
    _INDIANAPOLIS_SUB_SECTION_PARSER_EXPORT_KEY = "indianapolis_only_constructors"
    _PRIVATEER_SUB_SECTION_PARSER_EXPORT_KEY = "privateer_teams"
    _SUPPORTED_EXPORT_SCOPES = {
        "all",
        "current",
        "former",
        "indianapolis",
        "privateer",
    }
    _PARSE_SCOPE_CACHE: dict[tuple[bool, bool], dict[str, list[dict[str, Any]]]] = {}

    def __init__(self, *args: Any, export_scope: str = "all", **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if export_scope not in self._SUPPORTED_EXPORT_SCOPES:
            msg = (
                f"Unsupported export_scope='{export_scope}' "
                f"for {self.__class__.__name__}"
            )
            raise ValueError(msg)
        self._export_scope = export_scope
        self._split_export_records: dict[str, list[dict[str, Any]]] = {
            self._CURRENT_SECTION_PARSER_EXPORT_KEY: [],
            self._FORMER_SECTION_PARSER_EXPORT_KEY: [],
            self._INDIANAPOLIS_SUB_SECTION_PARSER_EXPORT_KEY: [],
            self._PRIVATEER_SUB_SECTION_PARSER_EXPORT_KEY: [],
        }

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        cache_key = (self.include_urls, self.normalize_empty_values)
        cached_scopes = self._PARSE_SCOPE_CACHE.get(cache_key)
        if cached_scopes is not None:
            logger.warning("ConstructorsListScraper: using cached parse flow.")
            self._restore_split_export_records(cached_scopes)
            return deepcopy(cached_scopes[self._export_scope])

        selector = WikipediaSectionByIdSelectionStrategy(domain="constructors")
        logger.warning("ConstructorsListScraper: starting parse flow.")
        current_records = self._parse_current_section(selector=selector, soup=soup)
        former_records, indianapolis_records = self._parse_former_sections(
            selector=selector,
            soup=soup,
        )
        privateer_records = self._parse_privateer_section(
            selector=selector,
            soup=soup,
        )
        scope_records = {
            "all": [
                *current_records,
                *former_records,
                *indianapolis_records,
                *privateer_records,
            ],
            "current": current_records,
            "former": former_records,
            "indianapolis": indianapolis_records,
            "privateer": privateer_records,
        }
        self._PARSE_SCOPE_CACHE[cache_key] = deepcopy(scope_records)
        self._restore_split_export_records(scope_records)
        logger.warning(
            "ConstructorsListScraper: parse flow finished, total records=%d.",
            len(scope_records["all"]),
        )

        return deepcopy(scope_records[self._export_scope])

    def _parse_current_section(
        self,
        *,
        selector: WikipediaSectionByIdSelectionStrategy,
        soup: BeautifulSoup,
    ) -> list[dict[str, Any]]:
        self._split_export_records[self._CURRENT_SECTION_PARSER_EXPORT_KEY] = []
        current_section = self._extract_current_section(selector=selector, soup=soup)
        if current_section is None:
            logger.warning(
                "ConstructorsListScraper: current section not found (ids=%s).",
                self._CURRENT_SECTION_FALLBACK_IDS,
            )
            return []
        logger.warning(
            "ConstructorsListScraper: current section found (ids=%s).",
            self._CURRENT_SECTION_FALLBACK_IDS,
        )
        current_parser = CurrentConstructorsSectionParser(
            config=self._CURRENT_CONFIG,
            section_label=self._CURRENT_SECTION_LABEL,
            include_urls=self.include_urls,
            normalize_empty_values=self.normalize_empty_values,
        )
        current_records = current_parser.parse(current_section).records
        logger.warning(
            "ConstructorsListScraper: current section parsed, records=%d.",
            len(current_records),
        )
        self._split_export_records[self._CURRENT_SECTION_PARSER_EXPORT_KEY].extend(
            current_records,
        )
        return current_records

    def _parse_former_sections(
        self,
        *,
        selector: WikipediaSectionByIdSelectionStrategy,
        soup: BeautifulSoup,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        former_section = selector.extract_section_by_id(
            soup,
            self._FORMER_SECTION_ID,
            domain="constructors",
        )
        if former_section is None:
            return ([], [])
        logger.warning("ConstructorsListScraper: former section found.")
        former_parser = FormerConstructorsSectionParser(
            config=self._FORMER_CONFIG,
            section_label=self._FORMER_SECTION_LABEL,
            include_urls=self.include_urls,
            normalize_empty_values=self.normalize_empty_values,
        )
        former_records = former_parser.parse(former_section).records
        logger.warning(
            "ConstructorsListScraper: former section parsed, records=%d.",
            len(former_records),
        )
        self._split_export_records[self._FORMER_SECTION_PARSER_EXPORT_KEY].extend(
            former_records,
        )
        indianapolis_records = former_parser.parse_indianapolis_only_records(
            former_section,
        )
        logger.warning(
            "ConstructorsListScraper: indianapolis-only extracted, records=%d.",
            len(indianapolis_records),
        )
        self._split_export_records[
            self._INDIANAPOLIS_SUB_SECTION_PARSER_EXPORT_KEY
        ].extend(
            indianapolis_records,
        )
        return (former_records, indianapolis_records)

    def _parse_privateer_section(
        self,
        *,
        selector: WikipediaSectionByIdSelectionStrategy,
        soup: BeautifulSoup,
    ) -> list[dict[str, Any]]:
        privateer_section = selector.extract_section_by_id(
            soup,
            self._PRIVATEER_SECTION_ID,
            domain="constructors",
        )
        if privateer_section is None:
            return []
        logger.warning("ConstructorsListScraper: privateer section found.")
        privateer_parser = PrivateerTeamsSectionParser()
        privateer_records = privateer_parser.parse(privateer_section).get("items", [])
        self._normalize_privateer_urls(privateer_records)
        self._split_export_records[
            self._PRIVATEER_SUB_SECTION_PARSER_EXPORT_KEY
        ].extend(
            privateer_records,
        )
        logger.warning(
            "ConstructorsListScraper: privateer section parsed, records=%d.",
            len(privateer_records),
        )
        return privateer_records

    def _restore_split_export_records(
        self,
        scope_records: dict[str, list[dict[str, Any]]],
    ) -> None:
        self._split_export_records = {
            self._CURRENT_SECTION_PARSER_EXPORT_KEY: list(scope_records["current"]),
            self._FORMER_SECTION_PARSER_EXPORT_KEY: list(scope_records["former"]),
            self._INDIANAPOLIS_SUB_SECTION_PARSER_EXPORT_KEY: list(
                scope_records["indianapolis"],
            ),
            self._PRIVATEER_SUB_SECTION_PARSER_EXPORT_KEY: list(
                scope_records["privateer"],
            ),
        }

    def _normalize_privateer_urls(self, privateer_records: list[Any]) -> None:
        if not self.include_urls:
            for record in privateer_records:
                if isinstance(record, dict):
                    record.pop("team_url", None)
            return
        for record in privateer_records:
            if not isinstance(record, dict):
                continue
            url = record.get("team_url")
            if isinstance(url, str) and url.startswith("/"):
                record["team_url"] = self._full_url(url)

    def _extract_current_section(
        self,
        *,
        selector: WikipediaSectionByIdSelectionStrategy,
        soup: BeautifulSoup,
    ) -> BeautifulSoup | None:
        for section_id in self._CURRENT_SECTION_FALLBACK_IDS:
            logger.warning(
                "ConstructorsListScraper: trying current section_id='%s'.",
                section_id,
            )
            section = selector.extract_section_by_id(
                soup,
                section_id,
                domain="constructors",
            )
            if section is not None:
                logger.warning(
                    "ConstructorsListScraper: section matched for section_id='%s'.",
                    section_id,
                )
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
        return output_path.with_name(
            f"{output_path.stem}_{parser_kind}{output_path.suffix}",
        )
