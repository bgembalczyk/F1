from __future__ import annotations

import re
from typing import Any, Dict, List

from bs4 import BeautifulSoup, Tag

from scrapers.base.options import ScraperOptions, init_scraper_options
from scrapers.base.scraper import F1Scraper
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.circuit_location import LocationColumn
from scrapers.base.table.columns.types.constructor_part import ConstructorPartColumn
from scrapers.base.table.columns.types.driver_list import DriverListColumn
from scrapers.base.table.columns.types.multi import MultiColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.parser import HtmlTableParser
from scrapers.base.table.pipeline import TablePipeline
from scrapers.grands_prix.helpers.article_validation import is_grand_prix_article


class F1SingleGrandPrixScraper(F1Scraper):
    """
    Scraper pojedynczego Grand Prix – pobiera tabelę "By year" z artykułu Wikipedii.

    Jeśli artykuł nie wygląda na Grand Prix (brak navboxa/kategorii),
    zwraca pustą listę.
    """

    _SKIP = object()
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
        options.with_fetcher()

        super().__init__(options=options)
        self.policy = options.to_http_policy()
        self.timeout = self.policy.timeout
        self.url: str = ""

    def fetch_html(self, url: str) -> str:
        return self.source_adapter.get(url, timeout=self.timeout)

    def fetch_by_url(self, url: str) -> List[Dict[str, Any]]:
        self.url = url
        return super().fetch()

    def _build_pipeline(self, section_id: str) -> TablePipeline:
        config = ScraperConfig(
            url=self.url,
            section_id=section_id,
            expected_headers=["Year", "Driver", "Constructor", "Report"],
            column_map={
                "Year": "year",
                "Driver": "driver",
                "Constructor": "constructor",
                "Report": "report",
                "Location": "location",
            },
            columns={
                "year": UrlColumn(),
                "driver": DriverListColumn(),
                "constructor": MultiColumn(
                    {
                        "chassis_constructor": ConstructorPartColumn(0),
                        "engine_constructor": ConstructorPartColumn(1),
                    }
                ),
                "report": AutoColumn(),
                "location": LocationColumn(),
            },
        )
        return TablePipeline(
            config=config,
            include_urls=self.include_urls,
            skip_sentinel=self._SKIP,
        )

    def _parse_section_table(
        self,
        soup: BeautifulSoup,
        *,
        section_id: str,
    ) -> List[Dict[str, Any]]:
        pipeline = self._build_pipeline(section_id)
        parser = HtmlTableParser(
            section_id=pipeline.section_id,
            fragment=pipeline.fragment,
            expected_headers=pipeline.expected_headers,
            table_css_class=pipeline.table_css_class,
        )
        records: List[Dict[str, Any]] = []
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
        normalized = value.lower()
        if len(normalized) == 3:
            return "".join(ch * 2 for ch in normalized)
        return normalized

    def _is_not_held_record(self, record: Dict[str, Any]) -> bool:
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

        if self._is_cancellation_context(report_text, layout_text):
            return True

        return False

    @staticmethod
    def _is_cancellation_context(
        report_text: str | None, layout_text: str | None
    ) -> bool:
        if report_text and report_text.lower().startswith("not held"):
            return True
        if not layout_text:
            return False
        layout_lower = layout_text.lower()
        return layout_lower.startswith("not held due to") or layout_lower.startswith(
            "cancelled due to"
        )

    @staticmethod
    def _get_text(value: Any) -> str | None:
        if isinstance(value, dict):
            text = value.get("text")
            if isinstance(text, str):
                return text
        if isinstance(value, str):
            return value
        return None

    def _list_text(self, items: Any) -> str | None:
        if not isinstance(items, list) or not items:
            return None
        first_text = self._get_text(items[0])
        if not first_text:
            return None
        if all(self._get_text(item) == first_text for item in items):
            return first_text
        return None

    def parse(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        if not is_grand_prix_article(soup):
            return []

        for section_id in [
            "By_year",
            "Winners",
            "By_year:_the_European_Grand_Prix_as_a_standalone_event",
            "Winners_of_the_Caesars_Palace_Grand_Prix",
        ]:
            try:
                return [
                    {
                        "url": self.url,
                        "by_year": self._parse_section_table(
                            soup,
                            section_id=section_id,
                        ),
                    }
                ]
            except RuntimeError:
                continue

        return [
            {
                "url": self.url,
                "by_year": [],
            }
        ]
