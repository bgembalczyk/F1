from __future__ import annotations

from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from models.records.link import LinkRecord
from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.text_normalization import clean_wiki_text
from scrapers.base.options import ScraperOptions, init_scraper_options
from scrapers.base.scraper import F1Scraper
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.driver import DriverColumn
from scrapers.base.table.columns.types.func import FuncColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.multi import MultiColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.pipeline import TablePipeline
from scrapers.grands_prix.helpers.article_validation import is_grand_prix_article


class ConstructorPartColumn(FuncColumn):
    def __init__(self, index: int) -> None:
        super().__init__(lambda ctx: _extract_constructor_part(ctx, index))


def _extract_constructor_part(ctx, index: int) -> LinkRecord | None:
    links = normalize_links(ctx.links, strip_marks=True, drop_empty=True)
    clean_text = clean_wiki_text(ctx.clean_text or "")

    if links:
        if "-" in clean_text and len(links) >= 2:
            return links[index] if index < len(links) else None
        if len(links) >= 2:
            return links[index] if index < len(links) else None
        return links[0]

    if not clean_text:
        return None

    if "-" in clean_text:
        parts = [part.strip() for part in clean_text.split("-", 1)]
        if len(parts) == 2:
            return {"text": parts[index] if index < len(parts) else parts[0], "url": None}

    return {"text": clean_text, "url": None}


def _extract_layout_text(clean_text: str, link_text: str) -> Optional[str]:
    if not clean_text:
        return None

    if link_text:
        lower_clean = clean_text.lower()
        lower_link = link_text.lower()
        idx = lower_clean.find(lower_link)
        if idx != -1:
            clean_text = (clean_text[:idx] + clean_text[idx + len(link_text) :]).strip()

    clean_text = clean_text.strip(" -–—()")
    if not clean_text:
        return None

    if link_text and clean_text.lower() == link_text.lower():
        return None

    return clean_text


class LocationColumn(FuncColumn):
    def __init__(self) -> None:
        super().__init__(self._parse_location)

    def _parse_location(self, ctx) -> Dict[str, Any] | None:
        links = normalize_links(ctx.links, strip_marks=True, drop_empty=True)
        clean_text = clean_wiki_text(ctx.clean_text or "")

        if not links and not clean_text:
            return None

        circuit: LinkRecord
        layout: Optional[str] = None

        if links:
            circuit = links[0]
            layout = _extract_layout_text(clean_text, circuit.get("text") or "")
        else:
            circuit = {"text": clean_text, "url": None}

        if layout:
            return {"circuit": circuit, "layout": layout}
        return {"circuit": circuit}


class F1SingleGrandPrixScraper(F1Scraper):
    """
    Scraper pojedynczego Grand Prix – pobiera tabelę "By year" z artykułu Wikipedii.

    Jeśli artykuł nie wygląda na Grand Prix (brak navboxa/kategorii),
    zwraca pustą listę.
    """

    _SKIP = object()

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

    def _build_pipeline(self) -> TablePipeline:
        config = ScraperConfig(
            url=self.url,
            section_id="By_year",
            expected_headers=["Year", "Driver", "Constructor", "Report"],
            column_map={
                "Year": "year",
                "Driver": "driver",
                "Constructor": "constructor",
                "Report": "report",
                "Location": "location",
            },
            columns={
                "year": IntColumn(),
                "driver": DriverColumn(),
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

    def _parse_by_year_table(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        pipeline = self._build_pipeline()
        return pipeline.parse_soup(soup)

    def parse(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        if not is_grand_prix_article(soup):
            return []

        try:
            by_year = self._parse_by_year_table(soup)
        except RuntimeError:
            by_year = []

        return [
            {
                "url": self.url,
                "by_year": by_year,
            }
        ]
