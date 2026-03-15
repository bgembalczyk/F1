import re
from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.options import ScraperOptions
from scrapers.seasons.parsers.calendar import SeasonCalendarParser
from scrapers.seasons.parsers.cancelled_rounds import CancelledRoundsParser
from scrapers.seasons.parsers.colin_chapman_trophy import ColinChapmanTrophyParser
from scrapers.seasons.parsers.adapters import SeasonParserAdapter
from scrapers.seasons.parsers.adapters import SeasonParsersPipeline
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
from scrapers.wiki.scraper import WikiScraper


class SingleSeasonScraper(WikiScraper):
    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        season_year: int | None = None,
    ) -> None:
        options = init_scraper_options(options, include_urls=True)
        policy = self.get_http_policy(options)
        options.with_fetcher(policy=policy)
        super().__init__(options=options, include_wiki_content=False)
        self.url: str = ""
        self.season_year = season_year
        self._options = options
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
        self.register_article_parser(
            SeasonParsersPipeline(parsers=self._build_domain_parsers()),
            target_key=None,
        )

    def _build_domain_parsers(self) -> list[SeasonParserAdapter]:
        def _calendar(soup: BeautifulSoup) -> list[dict[str, Any]]:
            return self._calendar_parser.parse(soup, self.season_year)

        return [
            SeasonParserAdapter(
                "entries",
                lambda soup: self._entries_parser.parse(soup, self.season_year),
            ),
            SeasonParserAdapter(
                "free_practice_drivers",
                lambda soup: self._free_practice_parser.parse(soup),
            ),
            SeasonParserAdapter("calendar", _calendar),
            SeasonParserAdapter(
                "cancelled_rounds",
                lambda soup: self._cancelled_rounds_parser.parse(
                    soup,
                    self.season_year,
                    _calendar(soup),
                ),
            ),
            SeasonParserAdapter(
                "testing_venues_and_dates",
                lambda soup: self._testing_venues_parser.parse(soup, self.season_year),
            ),
            SeasonParserAdapter("results", lambda soup: self._results_parser.parse(soup)),
            SeasonParserAdapter(
                "non_championship_races",
                lambda soup: self._non_championship_parser.parse(soup, self.season_year),
            ),
            SeasonParserAdapter(
                "scoring_system",
                lambda soup: self._scoring_system_parser.parse(soup),
            ),
            SeasonParserAdapter(
                "drivers_standings",
                lambda soup: self._standings_parser.parse_drivers(soup, self.season_year),
            ),
            SeasonParserAdapter(
                "constructors_standings",
                lambda soup: self._standings_parser.parse_constructors(soup),
            ),
            SeasonParserAdapter(
                "jim_clark_trophy",
                lambda soup: self._jim_clark_trophy_parser.parse(soup, self.season_year),
            ),
            SeasonParserAdapter(
                "colin_chapman_trophy",
                lambda soup: self._colin_chapman_trophy_parser.parse(
                    soup,
                    self.season_year,
                ),
            ),
            SeasonParserAdapter(
                "south_african_formula_one_championship",
                lambda soup: self._regional_parser.parse(
                    soup,
                    section_ids=["South_African_Formula_One_Championship"],
                    season_year=self.season_year,
                ),
            ),
            SeasonParserAdapter(
                "british_formula_one_championship",
                lambda soup: self._regional_parser.parse(
                    soup,
                    section_ids=["British_Formula_One_Championship"],
                    season_year=self.season_year,
                ),
            ),
        ]

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

    @staticmethod
    def _extract_year_from_url(url: str) -> int | None:
        match = re.search(r"/(\\d{4})_Formula_One", url)
        if match:
            return int(match.group(1))
        return None
