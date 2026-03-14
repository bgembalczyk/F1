from typing import Any

from bs4 import Tag

from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.drivers.infobox.parsers.active_years_parser import ActiveYearsParser
from scrapers.drivers.infobox.parsers.best_finish_parser import BestFinishParser
from scrapers.drivers.infobox.parsers.car_numbers_parser import CarNumbersParser
from scrapers.drivers.infobox.parsers.championships_parser import ChampionshipsParser
from scrapers.drivers.infobox.parsers.collapsible_table_parser import (
    CollapsibleTableParser,
)
from scrapers.drivers.infobox.parsers.finished_season_parser import FinishedSeasonParser
from scrapers.drivers.infobox.parsers.licence_parser import LicenceParser
from scrapers.drivers.infobox.parsers.link_extractor import InfoboxLinkExtractor
from scrapers.drivers.infobox.parsers.nationality_parser import NationalityParser
from scrapers.drivers.infobox.parsers.numeric_parser import NumericParser
from scrapers.drivers.infobox.parsers.race_event_parser import RaceEventParser
from scrapers.drivers.infobox.parsers.table_parser import TableParser
from scrapers.drivers.infobox.parsers.teams_parser import TeamsParser


class InfoboxCellParser:
    """Parser for individual infobox cells.

    This class delegates complex parsing tasks to specialized helper classes:
    - NumericParser: for integer and float parsing
    - ActiveYearsParser: for active years and year range parsing
    - TeamsParser: for teams parsing
    - ChampionshipsParser: for championships and class wins parsing
    - CarNumbersParser: for car numbers parsing
    - NationalityParser: for nationality parsing
    - TableParser: for nested table parsing
    - CollapsibleTableParser: for collapsible career table parsing
    - RaceEventParser: for race event parsing
    - FinishedSeasonParser: for finished season parsing
    - LicenceParser: for racing licence parsing
    - BestFinishParser: for best finish result parsing
    """

    def __init__(
        self,
        *,
        include_urls: bool,
        link_extractor: InfoboxLinkExtractor,
    ) -> None:
        self._include_urls = include_urls
        self._link_extractor = link_extractor

        # Initialize specialized parsers (only those that need state/dependencies)
        self._active_years_parser = ActiveYearsParser(link_extractor)
        self._teams_parser = TeamsParser(link_extractor, include_urls=include_urls)
        self._championships_parser = ChampionshipsParser(link_extractor)
        self._table_parser = TableParser(link_extractor)
        self._race_event_parser = RaceEventParser(link_extractor)
        self._finished_season_parser = FinishedSeasonParser()
        self._licence_parser = LicenceParser(link_extractor)
        self._best_finish_parser = BestFinishParser(link_extractor)
        self._collapsible_table_parser = CollapsibleTableParser(self)
        self._nationality_parser = NationalityParser(link_extractor)

    def parse_cell(self, cell: Tag) -> dict[str, Any]:
        text = clean_infobox_text(cell.get_text(" ", strip=True))
        payload = {"text": text}
        if self._include_urls:
            payload["links"] = self._link_extractor.extract_links(cell)
        return payload

    def parse_active_years(self, cell: Tag) -> list[dict[str, Any]]:
        """Parse active years as a list of individual seasons with links.

        Handles cases like:
        - Individual years: 2002, 2005, 2007, 2008
        - Ranges: 2007-2008 (interpolates missing links)
        """
        return self._active_years_parser.parse_active_years(cell)

    def parse_teams(self, cell: Tag) -> list[Any]:
        return self._teams_parser.parse_teams(cell)

    @staticmethod
    def parse_entries(cell: Tag) -> dict[str, int | None]:
        return NumericParser.parse_entries(cell)

    @staticmethod
    def parse_int_cell(cell: Tag) -> int | None:
        return NumericParser.parse_int_cell(cell)

    def parse_championships(self, cell: Tag) -> dict[str, Any]:
        """Parse championships count with links.

        Handles cases like:
        - "1 (2014)" -> {count: 1, championships: [{text: "2014", url: ...}]}
        - "2 (2015, 2016)" -> {count: 2, championships: [...]}
        """
        return self._championships_parser.parse_championships(cell)

    def parse_class_wins(self, cell: Tag) -> dict[str, Any]:
        """Parse class wins count with year and link information.

        Similar to championships, handles cases like:
        - "6 (1969, 1975, 1976)" -> {count: 6, wins: [{year: 1969, url: ...}, ...]}
        """
        return self._championships_parser.parse_class_wins(cell)

    @staticmethod
    def parse_float_cell(cell: Tag) -> float | None:
        return NumericParser.parse_float_cell(cell)

    @staticmethod
    def parse_car_numbers(cell: Tag) -> list[dict[str, Any]]:
        return CarNumbersParser.parse_car_numbers(cell)

    def parse_best_finish(self, cell: Tag) -> dict[str, Any]:
        """Parse best finish field - delegates to BestFinishParser."""
        return self._best_finish_parser.parse_best_finish(cell)

    def parse_race_event(self, cell: Tag) -> list[dict[str, Any]]:
        """Parse race event fields (First/Last race, win, and entry).

        Returns a list of all links found in the cell.
        If no links are found, returns the text as a single-item list with text field.
        """
        return self._race_event_parser.parse_race_event(cell)

    def parse_finished_last_season(self, cell: Tag) -> dict[str, Any]:
        """Parse 'Finished last season' field.

        Example: "14th (62 pts)" -> {position: "14th", points: 62}
        """
        return self._finished_season_parser.parse_finished_last_season(cell)

    def parse_racing_licence(self, cell: Tag) -> list[dict[str, Any]]:
        """Parse 'Racing licence' field - delegates to LicenceParser."""
        return self._licence_parser.parse_racing_licence(cell)

    def parse_full_data(self, cell: Tag) -> dict[str, Any]:
        return self._table_parser.parse_full_data(cell, include_urls=self._include_urls)

    @staticmethod
    def parse_nested_table(table: Tag) -> dict[str, Any]:
        return TableParser.parse_nested_table(table)

    def parse_nationality(self, cell: Tag) -> list[str] | list[dict[str, Any]]:
        """Parse nationality field.

        Handles cases like:
        - "American or Italian" -> ["American", "Italian"]
        - "British" with link -> [{"text": "British", "url": "..."}]
        - "Federation of Rhodesia and Nyasaland (1963)" -> structured data
        """
        return self._nationality_parser.parse_nationality(cell)

    def parse_collapsible_career_table(self, table: Tag) -> dict[str, Any] | None:
        """Parse collapsible career statistics table (e.g., motorcycle racing).

        Example structure:
        <table class="mw-collapsible">
          <tr><th>Title</th></tr>
          <tr><th>Active years</th><td>1960-1964</td></tr>
          <tr><th>Starts</th><td>129</td></tr>
          ...
        </table>
        """
        return self._collapsible_table_parser.parse_collapsible_career_table(table)
