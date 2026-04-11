from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from models.season_year import SeasonYear
from models.wiki_url import WikiUrl
from scrapers.adapters.section.adapter import SectionAdapter
from scrapers.domain_parsing_policy import DomainParsingPolicy
from scrapers.options import ScraperOptions
from scrapers.parsers.seasons.calendar import SeasonCalendarParser
from scrapers.parsers.seasons.cancelled_rounds import CancelledRoundsParser
from scrapers.parsers.seasons.colin_chapman_trophy import ColinChapmanTrophyParser
from scrapers.parsers.seasons.entries import SeasonEntriesParser
from scrapers.parsers.seasons.entry_merger import EntryMerger
from scrapers.parsers.seasons.free_practice import SeasonFreePracticeParser
from scrapers.parsers.seasons.jim_clark_trophy import JimClarkTrophyParser
from scrapers.parsers.seasons.non_championship import SeasonNonChampionshipParser
from scrapers.parsers.seasons.regional_championship import (
    SeasonRegionalChampionshipParser,
)
from scrapers.parsers.seasons.results import SeasonResultsParser
from scrapers.parsers.seasons.scoring_system import SeasonScoringSystemParser
from scrapers.parsers.seasons.table import SeasonTableParser
from scrapers.parsers.seasons.testing_venues import TestingVenuesParser
from scrapers.parsers.section.protocols.season import SeasonSectionParser
from scrapers.parsers.section.results.season import SeasonResultsSectionParser
from scrapers.parsers.section.season.calendar import SeasonCalendarSectionParser
from scrapers.parsers.section.standings.season.constructors import (
    SeasonConstructorsStandingsSectionParser,
)
from scrapers.parsers.section.standings.season.drivers import (
    SeasonDriversStandingsSectionParser,
)
from scrapers.records.sections.season import SeasonRecordSections
from scrapers.services.section.extraction.season_text import (
    SeasonTextSectionExtractionService,
)
from scrapers.services.section.factories.configurable import (
    ConfigurableSectionServiceFactory,
)
from scrapers.services.section.factories.section_service_factory import (
    SectionServiceFactory,
)

if TYPE_CHECKING:
    from typing import Any

    from bs4 import BeautifulSoup


class SeasonYearResolver:
    def resolve(
        self,
        *,
        url: WikiUrl | str,
        explicit_year: int | SeasonYear | None = None,
        current_year: int | SeasonYear | None = None,
    ) -> SeasonYear | None:
        if explicit_year is not None:
            return SeasonYear.from_raw(explicit_year)
        if current_year is not None:
            return SeasonYear.from_raw(current_year)
        return self.extract_from_url(url)

    @staticmethod
    def extract_from_url(url: WikiUrl | str) -> SeasonYear | None:
        if not url:
            return None
        resolved_url = WikiUrl.from_raw(url).to_export()
        match = re.search(r"/(\d{4})_Formula_One", resolved_url)
        if match:
            return SeasonYear(match.group(1))
        return None


@dataclass(frozen=True)
class SeasonSectionBinding:
    field_name: str
    parser: SeasonSectionParser


@dataclass(frozen=True)
class SeasonParserSet:
    table_parser: SeasonTableParser
    entries_parser: SeasonEntriesParser
    free_practice_parser: SeasonFreePracticeParser
    cancelled_rounds_parser: CancelledRoundsParser
    testing_venues_parser: TestingVenuesParser
    non_championship_parser: SeasonNonChampionshipParser
    scoring_system_parser: SeasonScoringSystemParser
    jim_clark_trophy_parser: JimClarkTrophyParser
    colin_chapman_trophy_parser: ColinChapmanTrophyParser
    regional_parser: SeasonRegionalChampionshipParser
    section_parsers: tuple[SeasonSectionBinding, ...]


# Backward-compatible alias.
SeasonParserSet = SeasonParsingComponents


class SeasonParsingComponentsBuilder:
    def __init__(
        self,
        *,
        options: ScraperOptions,
        include_urls: bool,
        policy: DomainParsingPolicy | None = None,
    ) -> None:
        self._options = options
        self._include_urls = include_urls
        self._policy = policy or DomainParsingPolicy()

    def build(self, *, url: str, season_year: int | None) -> SeasonParserSet:
        table_parser = SeasonTableParser(
            options=self._options,
            include_urls=self._include_urls,
            url=url,
        )
        standings_parser = SeasonStandingsService(table_parser)
        return SeasonParsingComponents(
            table_parser=table_parser,
            entries_parser=SeasonEntriesParser(
                table_parser,
                EntryMerger(),
                policy=self._policy,
            ),
            free_practice_parser=SeasonFreePracticeParser(table_parser),
            cancelled_rounds_parser=CancelledRoundsParser(table_parser),
            testing_venues_parser=TestingVenuesParser(
                table_parser,
                policy=self._policy,
            ),
            non_championship_parser=SeasonNonChampionshipParser(table_parser),
            scoring_system_parser=SeasonScoringSystemParser(table_parser),
            jim_clark_trophy_parser=JimClarkTrophyParser(table_parser),
            colin_chapman_trophy_parser=ColinChapmanTrophyParser(table_parser),
            regional_parser=SeasonRegionalChampionshipParser(table_parser),
            section_parsers=(
                SeasonSectionBinding(
                    field_name="calendar",
                    parser=SeasonCalendarSectionParser(
                        SeasonCalendarParser(table_parser),
                        season_year,
                    ),
                ),
                SeasonSectionBinding(
                    field_name="results",
                    parser=SeasonResultsSectionParser(
                        SeasonResultsParser(table_parser),
                    ),
                ),
                SeasonSectionBinding(
                    field_name="drivers_standings",
                    parser=SeasonDriversStandingsSectionParser(
                        standings_parser,
                        season_year,
                    ),
                ),
                SeasonSectionBinding(
                    field_name="constructors_standings",
                    parser=SeasonConstructorsStandingsSectionParser(
                        standings_parser,
                    ),
                ),
            ),
        )


class SeasonSectionDataCollector:
    def collect(
        self,
        *,
        soup: BeautifulSoup,
        parser_set: SeasonParsingComponents,
        season_year: int | None,
    ) -> SeasonRecordSections:
        section_records = self._collect_section_records(
            soup=soup,
            section_parsers=parser_set.section_parsers,
        )
        calendar_data = section_records["calendar"]
        return SeasonRecordSections(
            entries=parser_set.entries_parser.parse(soup, season_year),
            free_practice_drivers=parser_set.free_practice_parser.parse(soup),
            calendar=calendar_data,
            cancelled_rounds=parser_set.cancelled_rounds_parser.parse(
                soup,
                season_year,
                calendar_data,
            ),
            testing_venues_and_dates=parser_set.testing_venues_parser.parse(
                soup,
                season_year,
            ),
            results=section_records["results"],
            non_championship_races=parser_set.non_championship_parser.parse(
                soup,
                season_year,
            ),
            scoring_system=parser_set.scoring_system_parser.parse(soup),
            drivers_standings=section_records["drivers_standings"],
            constructors_standings=section_records["constructors_standings"],
            jim_clark_trophy=parser_set.jim_clark_trophy_parser.parse(
                soup,
                season_year,
            ),
            colin_chapman_trophy=parser_set.colin_chapman_trophy_parser.parse(
                soup,
                season_year,
            ),
            south_african_formula_one_championship=parser_set.regional_parser.parse(
                soup,
                section_ids=["South_African_Formula_One_Championship"],
                season_year=season_year,
            ),
            british_formula_one_championship=parser_set.regional_parser.parse(
                soup,
                section_ids=["British_Formula_One_Championship"],
                season_year=season_year,
            ),
            regulation_changes=[],
            mid_season_changes=[],
        )

    def _collect_section_records(
        self,
        *,
        soup: BeautifulSoup,
        section_parsers: tuple[SeasonSectionBinding, ...],
    ) -> dict[str, list[dict[str, Any]]]:
        return {
            binding.field_name: binding.parser.parse(soup).records
            for binding in section_parsers
        }


class SeasonSectionPipeline:
    def __init__(
        self,
        *,
        parser_set_builder: SeasonParsingComponentsBuilder,
        section_data_collector: SeasonSectionDataCollector | None = None,
        text_sections_service_factory: (
            SectionServiceFactory[SeasonTextSectionExtractionService] | None
        ) = None,
    ) -> None:
        self._parser_set_builder = parser_set_builder
        self._section_data_collector = (
            section_data_collector or SeasonSectionDataCollector()
        )
        self._text_sections_service_factory = text_sections_service_factory or (
            ConfigurableSectionServiceFactory(
                service_cls=SeasonTextSectionExtractionService,
                require_options=False,
                require_url=False,
                pass_options=False,
                pass_url=False,
            )
        )
        self._parser_set: SeasonParsingComponents | None = None
        self._url = ""
        self._season_year: int | None = None

    @property
    def table_parser(self) -> SeasonTableParser | None:
        if self._parser_set is None:
            return None
        return self._parser_set.table_parser

    def configure(self, *, url: str, season_year: int | None) -> None:
        self._url = url
        self._season_year = season_year
        self._parser_set = self._parser_set_builder.build(
            url=url,
            season_year=season_year,
        )

    def collect(
        self,
        *,
        soup: BeautifulSoup,
        adapter: SectionAdapter,
    ) -> SeasonRecordSections:
        parser_set = self._require_parser_set()
        text_records = self._text_sections_service_factory.create(
            adapter=adapter,
            options=parser_set.table_parser.options,
            url=self._url,
        ).extract(soup)
        section_data = self._section_data_collector.collect(
            soup=soup,
            parser_set=parser_set,
            season_year=self._season_year,
        )
        return SeasonRecordSections(
            entries=section_data.entries,
            free_practice_drivers=section_data.free_practice_drivers,
            calendar=section_data.calendar,
            cancelled_rounds=section_data.cancelled_rounds,
            testing_venues_and_dates=section_data.testing_venues_and_dates,
            results=section_data.results,
            non_championship_races=section_data.non_championship_races,
            scoring_system=section_data.scoring_system,
            drivers_standings=section_data.drivers_standings,
            constructors_standings=section_data.constructors_standings,
            jim_clark_trophy=section_data.jim_clark_trophy,
            colin_chapman_trophy=section_data.colin_chapman_trophy,
            south_african_formula_one_championship=(
                section_data.south_african_formula_one_championship
            ),
            british_formula_one_championship=(
                section_data.british_formula_one_championship
            ),
            regulation_changes=text_records.get("regulation_changes", []),
            mid_season_changes=text_records.get("mid-season_changes", []),
        )

    def _require_parser_set(self) -> SeasonParsingComponents:
        if self._parser_set is None:
            self.configure(url=self._url, season_year=self._season_year)
        if self._parser_set is None:
            msg = (
                "SeasonSectionPipeline requires parser configuration before collect()."
            )
            raise RuntimeError(msg)
        return self._parser_set
