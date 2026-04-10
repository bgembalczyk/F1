from __future__ import annotations

from bs4 import BeautifulSoup

from scrapers.infobox.extraction.factory import build_infobox_orchestrator
from scrapers.infobox.extraction.result import InfoboxExtractionResult
from scrapers.options import ScraperOptions


def extract_infobox(
    domain: str,
    soup: BeautifulSoup,
    *,
    url: str = "",
    options: ScraperOptions | None = None,
) -> InfoboxExtractionResult:
    orchestrator = build_infobox_orchestrator(domain, options=options)
    return orchestrator.extract(soup, url=url)
