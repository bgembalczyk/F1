from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.abc import F1Scraper
from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.helpers.table_parsing import TableParsingHelper
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.mixins.wiki_sections import WikipediaSectionByIdMixin
from scrapers.base.options import ScraperOptions
from scrapers.base.records import record_from_mapping
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.constructor import ConstructorColumn
from scrapers.base.table.columns.types.driver_list import DriverListColumn
from scrapers.base.table.columns.types.engine import EngineColumn
from scrapers.base.table.columns.types.entrant import EntrantColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.position import PositionColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.columns.types.tyre import TyreColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.base.table.pipeline import TablePipeline
from scrapers.drivers.columns.points_or_text import PointsOrTextColumn
from scrapers.drivers.columns.round import RoundColumn
from scrapers.drivers.columns.series import SeriesColumn
from scrapers.drivers.columns.unknown_value import UnknownValueColumn
from scrapers.drivers.infobox.scraper import DriverInfoboxScraper


class SingleDriverScraper(WikipediaSectionByIdMixin, F1Scraper):
    _UNKNOWN_VALUE = "unknown"

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
    ) -> None:
        options = init_scraper_options(options, include_urls=True)
        policy = self.get_http_policy(options)
        options.with_fetcher(policy=policy)
        super().__init__(options=options)
        self.policy = self.http_policy
        self.url: str = ""
        self.debug_dir = options.debug_dir

    def fetch_by_url(self, url: str) -> list[dict[str, Any]]:
        self.url = url
        return super().fetch()

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        return [
            {
                "url": self.url,
                "infobox": self._scrape_infobox(soup),
                "career_results": self._parse_results_sections(soup),
            },
        ]

    def _scrape_infobox(self, soup: BeautifulSoup) -> dict[str, Any]:
        infobox_scraper = DriverInfoboxScraper(
            options=ScraperOptions(
                include_urls=self.include_urls,
                debug_dir=self.debug_dir,
            ),
            run_id=getattr(self, "_run_id", None),
            url=self.url,
        )
        records = infobox_scraper.parse(soup)
        return records[0] if records else {}

    def _parse_results_sections(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        sections = [
            "Career results",
            "Karting record",
            "Racing record",
        ]
        records: list[dict[str, Any]] = []

        for section_title in sections:
            section_soup = self.extract_section_by_id(
                soup,
                section_title.replace(" ", "_"),
            )
            if section_soup is None:
                continue

            for table in section_soup.find_all("table", class_="wikitable"):
                table_meta = self._table_context(table, section_title)
                parsed = self._parse_results_table(table)
                if parsed:
                    parsed.update(table_meta)
                    records.append(parsed)

        return records

    def _table_context(self, table: Tag, section_title: str) -> dict[str, Any]:
        return {
            "section": section_title,
            "heading_path": self._heading_context(table),
        }

    def _heading_context(self, table: Tag) -> list[str]:
        headings: list[str] = []
        node = table
        while node is not None:
            node = node.previous_sibling
            if not isinstance(node, Tag):
                continue

            heading_tag = None
            if node.name in {"h2", "h3", "h4", "h5"}:
                heading_tag = node
            elif "mw-heading" in (node.get("class") or []):
                heading_tag = node.find(["h2", "h3", "h4", "h5"], recursive=False)

            if heading_tag is None:
                continue

            text = clean_wiki_text(heading_tag.get_text(" ", strip=True))
            if text:
                headings.append(text)
            if heading_tag.name == "h2":
                break

        headings.reverse()
        return headings

    def _parse_results_table(self, table: Tag) -> dict[str, Any] | None:
        headers = self._extract_headers(table)
        if not headers:
            return None

        header_set = set(headers)
        if {"Season", "Series", "Position", "Team", "Car"}.issubset(header_set):
            return {
                "table_type": "career_highlights",
                "headers": headers,
                "rows": self._parse_career_highlights(table),
            }

        if {"Season", "Series", "Position"}.issubset(header_set):
            return {
                "table_type": "career_summary",
                "headers": headers,
                "rows": self._parse_career_summary(table),
            }

        if "Year" in header_set:
            return {
                "table_type": "results_by_year",
                "headers": headers,
                "rows": self._parse_complete_results(table, headers),
            }

        return None

    def _parse_career_highlights(self, table: Tag) -> list[dict[str, Any]]:
        schema = TableSchemaDSL(
            columns=[
                column("Season", "season", self._unknown(IntColumn())),
                column("Series", "series", self._unknown(UrlColumn())),
                column("Position", "position", self._unknown(PositionColumn())),
                column("Team", "team", self._unknown(EntrantColumn())),
                column("Car", "car", self._unknown(UrlColumn())),
            ],
        )
        pipeline = self._build_pipeline(schema=schema)
        return self._parse_table(table, pipeline)

    def _parse_career_summary(self, table: Tag) -> list[dict[str, Any]]:
        schema = TableSchemaDSL(
            columns=[
                column("Season", "season", self._unknown(IntColumn())),
                column("Series", "series", self._unknown(SeriesColumn())),
                column("Position", "position", self._unknown(TextColumn())),
                column("Team", "team", self._unknown(EntrantColumn())),
                column("Races", "races", self._unknown(IntColumn())),
                column("Wins", "wins", self._unknown(IntColumn())),
                column("Poles", "poles", self._unknown(IntColumn())),
                column("F/Laps", "fastest_laps", self._unknown(IntColumn())),
                column("F/Lap", "fastest_laps", self._unknown(IntColumn())),
                column("Podiums", "podiums", self._unknown(IntColumn())),
                column("Points", "points", self._unknown(PointsOrTextColumn())),
            ],
        )
        pipeline = self._build_pipeline(schema=schema)
        return self._parse_table(table, pipeline)

    def _parse_complete_results(
        self,
        table: Tag,
        headers: list[str],
    ) -> list[dict[str, Any]]:
        column_map = {
            "Year": "year",
            "Team": "team",
            "Co-Drivers": "co_drivers",
            "Co-drivers": "co_drivers",
            "Car": "car",
            "Class": "class",
            "Laps": "laps",
            "Pos.": "pos",
            "Pos": "pos",
            "Class Pos.": "class_pos",
            "Class Pos": "class_pos",
            "Entrant": "entrant",
            "Chassis": "chassis",
            "Engine": "engine",
            "WDC": "wdc",
            "Points": "points",
            "Rank": "rank",
            "DC": "dc",
            "Qualifying": "qualifying",
            "Quali Race": "quali_race",
            "Main race": "main_race",
            "Tyres": "tyres",
            "No.": "no",
            "No": "no",
            "Start": "start",
            "Finish": "finish",
            "Stages won": "stages_won",
            "Pts": "points",
            "Pts.": "points",
            "Ref": "ref",
            "Make": "make",
            "Manufacturer": "manufacturer",
            "NGNC": "ngnc",
            "QH": "qh",
            "F": "f",
        }
        columns: dict[str, Any] = {
            "year": self._unknown(AutoColumn()),
            "team": self._unknown(EntrantColumn()),
            "co_drivers": self._unknown(DriverListColumn()),
            "car": self._unknown(AutoColumn()),
            "class": self._unknown(AutoColumn()),
            "laps": self._unknown(IntColumn()),
            "pos": self._unknown(PositionColumn()),
            "class_pos": self._unknown(PositionColumn()),
            "entrant": self._unknown(EntrantColumn()),
            "chassis": self._unknown(LinksListColumn(text_for_missing_url=True)),
            "engine": self._unknown(EngineColumn()),
            "wdc": self._unknown(PositionColumn()),
            "points": self._unknown(PointsOrTextColumn()),
            "rank": self._unknown(PositionColumn()),
            "dc": self._unknown(PositionColumn()),
            "qualifying": self._unknown(PositionColumn()),
            "quali_race": self._unknown(PositionColumn()),
            "main_race": self._unknown(PositionColumn()),
            "tyres": self._unknown(TyreColumn()),
            "no": self._unknown(IntColumn()),
            "start": self._unknown(PositionColumn()),
            "finish": self._unknown(PositionColumn()),
            "stages_won": self._unknown(IntColumn()),
            "make": self._unknown(ConstructorColumn()),
            "manufacturer": self._unknown(ConstructorColumn()),
            "ngnc": self._unknown(PositionColumn()),
            "qh": self._unknown(PositionColumn()),
            "f": self._unknown(PositionColumn()),
            "ref": SkipColumn(),
        }

        schema_columns = [
            column(header, key, columns[key]) for header, key in column_map.items()
        ]
        schema_columns.extend(
            [
                column(header, header, self._unknown(RoundColumn()))
                for header in headers
                if header.isdigit()
            ],
        )

        pipeline = self._build_pipeline(schema=TableSchemaDSL(columns=schema_columns))
        return self._parse_table(table, pipeline)

    def _parse_table(
        self,
        table: Tag,
        pipeline: TablePipeline,
    ) -> list[dict[str, Any]]:
        return TableParsingHelper.parse_table_with_pipeline(table, pipeline)

    def _build_pipeline(
        self,
        *,
        schema: TableSchemaDSL,
    ) -> TablePipeline:
        config = ScraperConfig(
            url=self.url,
            section_id=None,
            expected_headers=None,
            schema=schema,
            default_column=AutoColumn(),
            record_factory=record_from_mapping,
        )
        return TablePipeline(
            config=config,
            include_urls=self.include_urls,
            normalize_empty_values=self.normalize_empty_values,
            debug_dir=self.debug_dir,
        )

    def _extract_headers(self, table: Tag) -> list[str]:
        header_row = table.find("tr")
        if not header_row:
            return []
        header_cells = header_row.find_all(["th", "td"])
        return [clean_wiki_text(c.get_text(" ", strip=True)) for c in header_cells]

    def _unknown(self, column: Any) -> UnknownValueColumn:
        return UnknownValueColumn(column, unknown_value=self._UNKNOWN_VALUE)
