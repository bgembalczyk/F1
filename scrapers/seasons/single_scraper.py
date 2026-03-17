import re
from collections.abc import Callable
from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.options import ScraperOptions
from scrapers.base.sections.adapter import SectionAdapter
from scrapers.base.single_wiki_article import SingleWikiArticleSectionAdapterBase
from scrapers.seasons.parsers.calendar import SeasonCalendarParser
from scrapers.seasons.parsers.cancelled_rounds import CancelledRoundsParser
from scrapers.seasons.parsers.colin_chapman_trophy import ColinChapmanTrophyParser
from scrapers.seasons.parsers.entries import SeasonEntriesParser
from scrapers.seasons.parsers.entry_merger import EntryMerger
from scrapers.seasons.parsers.free_practice import SeasonFreePracticeParser
from scrapers.seasons.parsers.jim_clark_trophy import JimClarkTrophyParser
from scrapers.seasons.parsers.non_championship import SeasonNonChampionshipParser
from scrapers.seasons.parsers.regional_championship import (
    SeasonRegionalChampionshipParser,
)
from scrapers.seasons.parsers.results import SeasonResultsParser
from scrapers.seasons.parsers.scoring_system import SeasonScoringSystemParser
from scrapers.seasons.parsers.standings import SeasonStandingsParser
from scrapers.seasons.parsers.table import SeasonTableParser
from scrapers.seasons.parsers.testing_venues import TestingVenuesParser
from scrapers.seasons.postprocess.assembler import SeasonRecordAssembler
from scrapers.seasons.postprocess.assembler import SeasonRecordSections
from scrapers.seasons.postprocess.contract import SeasonSectionContractPostProcessor
from scrapers.seasons.sections.calendar import SeasonCalendarSectionParser
from scrapers.seasons.sections.results import SeasonResultsSectionParser
from scrapers.seasons.sections.service import SeasonTextSectionExtractionService
from scrapers.seasons.sections.standings import SeasonConstructorsStandingsSectionParser
from scrapers.seasons.sections.standings import SeasonDriversStandingsSectionParser


class SingleSeasonScraper(SingleWikiArticleSectionAdapterBase):
    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        season_year: int | None = None,
        text_sections_service_factory: (
            Callable[[SectionAdapter], SeasonTextSectionExtractionService] | None
        ) = None,
        assembler: SeasonRecordAssembler | None = None,
    ) -> None:
        super().__init__(options=options)
        self.season_year = season_year
        self._entry_merger = EntryMerger()
        self._table_parser = SeasonTableParser(
            options=self._options,
            include_urls=self.include_urls,
            url=self.url,
        )
        self._entries_parser = SeasonEntriesParser(
            self._table_parser,
            self._entry_merger,
        )
        self._free_practice_parser = SeasonFreePracticeParser(self._table_parser)
        self._calendar_parser = SeasonCalendarParser(self._table_parser)
        self._cancelled_rounds_parser = CancelledRoundsParser(self._table_parser)
        self._testing_venues_parser = TestingVenuesParser(self._table_parser)
        self._results_parser = SeasonResultsParser(self._table_parser)
        self._non_championship_parser = SeasonNonChampionshipParser(self._table_parser)
        self._scoring_system_parser = SeasonScoringSystemParser(self._table_parser)
        self._standings_parser = SeasonStandingsParser(self._table_parser)
        self._jim_clark_trophy_parser = JimClarkTrophyParser(self._table_parser)
        self._colin_chapman_trophy_parser = ColinChapmanTrophyParser(self._table_parser)
        self._regional_parser = SeasonRegionalChampionshipParser(self._table_parser)
        self._text_sections_service_factory = text_sections_service_factory or (
            lambda adapter: SeasonTextSectionExtractionService(adapter=adapter)
        )
        self._assembler = assembler or SeasonRecordAssembler()

    def fetch_by_url(
        self,
        url: str,
        *,
        season_year: int | None = None,
    ) -> list[dict[str, Any]]:
        self.url = url
        self._table_parser.update_url(url)
        if season_year is not None:
            self.season_year = season_year
        elif self.season_year is None:
            self.season_year = self._extract_year_from_url(url)
        return super().fetch()

    def _build_post_processor(self) -> SeasonSectionContractPostProcessor:
        return SeasonSectionContractPostProcessor()

    def _build_infobox_payload(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        _ = soup
        return []

    def _build_sections_payload(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        text_records = self._text_sections_service_factory(self).extract(soup)
        return [
            {
                "regulation_changes": text_records.get("Regulation_changes", []),
                "mid_season_changes": text_records.get("Mid-season_changes", []),
            },
        ]

    def _assemble_record(
        self,
        *,
        soup: BeautifulSoup,
        infobox_payload: list[dict[str, Any]],
        sections_payload: list[dict[str, Any]],
    ) -> dict[str, Any]:
        _ = infobox_payload
        text_payload = sections_payload[0] if sections_payload else {}
        calendar_data = (
            SeasonCalendarSectionParser(self._calendar_parser, self.season_year)
            .parse(soup)
            .records
        )
        results_data = (
            SeasonResultsSectionParser(self._results_parser).parse(soup).records
        )
        drivers_standings = (
            SeasonDriversStandingsSectionParser(
                self._standings_parser,
                self.season_year,
            )
            .parse(soup)
            .records
        )
        constructors_standings = (
            SeasonConstructorsStandingsSectionParser(self._standings_parser)
            .parse(soup)
            .records
        )

        sections = SeasonRecordSections(
            entries=self._entries_parser.parse(soup, self.season_year),
            free_practice_drivers=self._free_practice_parser.parse(soup),
            calendar=calendar_data,
            cancelled_rounds=self._cancelled_rounds_parser.parse(
                soup,
                self.season_year,
                calendar_data,
            ),
            testing_venues_and_dates=self._testing_venues_parser.parse(
                soup,
                self.season_year,
            ),
            results=results_data,
            non_championship_races=self._non_championship_parser.parse(
                soup,
                self.season_year,
            ),
            scoring_system=self._scoring_system_parser.parse(soup),
            drivers_standings=drivers_standings,
            constructors_standings=constructors_standings,
            jim_clark_trophy=self._jim_clark_trophy_parser.parse(
                soup,
                self.season_year,
            ),
            colin_chapman_trophy=self._colin_chapman_trophy_parser.parse(
                soup,
                self.season_year,
            ),
            south_african_formula_one_championship=self._regional_parser.parse(
                soup,
                section_ids=["South_African_Formula_One_Championship"],
                season_year=self.season_year,
            ),
            british_formula_one_championship=self._regional_parser.parse(
                soup,
                section_ids=["British_Formula_One_Championship"],
                season_year=self.season_year,
            ),
            regulation_changes=text_payload.get("regulation_changes", []),
            mid_season_changes=text_payload.get("mid_season_changes", []),
        )
        return self._assembler.assemble(sections)

    @staticmethod
    def _extract_year_from_url(url: str) -> int | None:
        match = re.search(r"/(\\d{4})_Formula_One", url)
        if match:
            return int(match.group(1))
        return None
