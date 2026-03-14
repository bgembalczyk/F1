from __future__ import annotations

import re
from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.abc import F1Scraper
from scrapers.base.errors import DomainParseError
from scrapers.base.errors import ScraperError
from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.helpers.normalize import normalize_auto_value
from scrapers.base.records import record_from_mapping
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.driver_list import DriverListColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.base.table.parser import HtmlTableParser
from scrapers.base.table.pipeline import TablePipeline
from scrapers.grands_prix.columns.circuit_location import LocationColumn
from scrapers.grands_prix.columns.constructor_split import ConstructorSplitColumn
from scrapers.grands_prix.helpers.article_validation import is_grand_prix_article

if TYPE_CHECKING:
    from bs4 import BeautifulSoup
    from bs4 import Tag

    from scrapers.base.options import ScraperOptions


class F1SingleGrandPrixScraper(F1Scraper):
    """
    Scraper pojedynczego Grand Prix - pobiera tabelę "By year" z artykułu Wikipedii.

    Jeśli artykuł nie wygląda na Grand Prix (brak navboxa/kategorii),
    zwraca pustą listę.
    """

    _BACKGROUND_HEX = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})")
    _BACKGROUND_MAP = {
        "ffffcc": "pre_war_european_championship",
        "d0ffb0": "pre_war_world_manufacturers_championship",
        "ffcccc": "non_championship",
    }
    _DEFAULT_CHAMPIONSHIP = "formula_one_world_championship"
    _UNKNOWN_CHAMPIONSHIP = "unknown"

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

    def fetch_by_url(self, url: str) -> list[dict[str, Any]]:
        self.url = url
        return super().fetch()

    def _build_pipeline(self, section_id: str) -> TablePipeline:
        schema = TableSchemaDSL(
            columns=[
                column("Year", "year", UrlColumn()),
                column("Driver", "driver", DriverListColumn()),
                column("Constructor", "constructor", ConstructorSplitColumn()),
                column("Report", "report", AutoColumn()),
                column("Location", "location", LocationColumn()),
            ],
        )
        config = ScraperConfig(
            url=self.url,
            section_id=section_id,
            expected_headers=["Year", "Driver", "Constructor", "Report"],
            schema=schema,
            record_factory=record_from_mapping,
        )
        return TablePipeline(
            config=config,
            include_urls=self.include_urls,
            normalize_empty_values=self.normalize_empty_values,
        )

    def _parse_section_table(
        self,
        soup: BeautifulSoup,
        *,
        section_id: str,
    ) -> list[dict[str, Any]]:
        pipeline = self._build_pipeline(section_id)
        parser = HtmlTableParser(
            section_id=pipeline.section_id,
            fragment=pipeline.fragment,
            expected_headers=pipeline.expected_headers,
            table_css_class=pipeline.table_css_class,
        )
        records: list[dict[str, Any]] = []
        for row_index, row in enumerate(parser.parse(soup)):
            record = pipeline.parse_cells(
                row.headers,
                row.cells,
                row_index=row_index,
            )
            if record:
                if self._is_not_held_record(record):
                    continue
                record["championship"] = self._championship_from_row(row.raw_tr)
                records.append(record)
        return records

    def _championship_from_row(self, row: Tag) -> str:
        color = self._background_color(row)
        if color is None:
            return self._DEFAULT_CHAMPIONSHIP
        return self._BACKGROUND_MAP.get(color, self._UNKNOWN_CHAMPIONSHIP)

    def _background_color(self, row: Tag) -> str | None:
        for candidate in [row.get("style"), row.get("bgcolor")]:
            color = self._extract_color(candidate)
            if color:
                return color
        for cell in row.find_all(["th", "td"], recursive=False):
            for candidate in [cell.get("style"), cell.get("bgcolor")]:
                color = self._extract_color(candidate)
                if color:
                    return color
        return None

    def _extract_color(self, candidate: str | None) -> str | None:
        if not candidate:
            return None
        match = self._BACKGROUND_HEX.search(candidate)
        if not match:
            return None
        return self._normalize_hex(match.group(1))

    @staticmethod
    def _normalize_hex(value: str) -> str:
        _hex_short_length = 3
        normalized = value.lower()
        if len(normalized) == _hex_short_length:
            return "".join(ch * 2 for ch in normalized)
        return normalized

    def _is_not_held_record(self, record: dict[str, Any]) -> bool:
        report_text = self._get_text(record.get("report"))
        location = record.get("location")
        layout_text = location.get("layout") if isinstance(location, dict) else None
        circuit_text = (
            self._get_text(location.get("circuit"))
            if isinstance(location, dict)
            else None
        )

        driver_text = self._list_text(record.get("driver"))
        chassis_text = self._get_text(record.get("chassis_constructor"))
        engine_text = self._get_text(record.get("engine_constructor"))

        if not all([driver_text, chassis_text, engine_text, circuit_text]):
            return False

        if not (driver_text == chassis_text == engine_text == circuit_text):
            return False

        if driver_text == "Not held":
            return True

        return bool(self._is_cancellation_context(report_text, layout_text))

    @staticmethod
    def _is_cancellation_context(
        report_text: str | None,
        layout_text: str | None,
    ) -> bool:
        if report_text and report_text.lower().startswith("not held"):
            return True
        if not layout_text:
            return False
        layout_lower = layout_text.lower()
        return layout_lower.startswith(("not held due to", "cancelled due to"))

    @staticmethod
    def _get_text(value: Any) -> str | None:
        normalized = normalize_auto_value(
            value,
            strip_marks=True,
            drop_empty=True,
        )
        if isinstance(normalized, dict):
            text = normalized.get("text")
            if isinstance(text, str) and text:
                return text
            return None
        if isinstance(normalized, str):
            return normalized or None
        return None

    def _list_text(self, items: Any) -> str | None:
        normalized = normalize_auto_value(
            items,
            strip_marks=True,
            drop_empty=True,
        )
        if not isinstance(normalized, list) or not normalized:
            return None
        first_text = self._get_text(normalized[0])
        if not first_text:
            return None
        if all(self._get_text(item) == first_text for item in normalized):
            return first_text
        return None

    def _try_parse_section(
        self,
        soup: BeautifulSoup,
        section_id: str,
    ) -> list[dict[str, Any]] | None:
        """Try to parse a section table.

        Returns None when the next section should be tried.
        """
        try:
            return [
                {
                    "url": self.url,
                    "by_year": self._parse_section_table(soup, section_id=section_id),
                },
            ]
        except Exception as exc:
            if isinstance(exc, RuntimeError):
                error: Exception = DomainParseError(
                    f"Brak sekcji {section_id!r} w artykule.",
                    url=self.url,
                    cause=exc,
                )
            else:
                error = (
                    exc
                    if isinstance(exc, ScraperError)
                    else self._wrap_parse_error(exc)
                )
            if self._handle_scraper_error(error):
                return None
            if error is exc:
                raise
            raise error from exc

    def parse(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        if not is_grand_prix_article(soup):
            return []

        for section_id in [
            "By_year",
            "Winners",
            "By_year:_the_European_Grand_Prix_as_a_standalone_event",
            "Winners_of_the_Caesars_Palace_Grand_Prix",
        ]:
            result = self._try_parse_section(soup, section_id)
            if result is not None:
                return result

        return [
            {
                "url": self.url,
                "by_year": [],
            },
        ]
