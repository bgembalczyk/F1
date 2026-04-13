from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.infobox.extraction.result import InfoboxExtractionResult

if TYPE_CHECKING:
    from bs4 import BeautifulSoup

    from scrapers.options import ScraperOptions


def extract_infobox(
    domain: str,
    soup: BeautifulSoup,
    *,
    url: str = "",
    options: ScraperOptions | None = None,
) -> InfoboxExtractionResult:
    from scrapers.infobox.extraction.factory import build_infobox_orchestrator

    orchestrator = build_infobox_orchestrator(domain, options=options)
    return orchestrator.extract(soup, url=url)


def __getattr__(name: str) -> object:
    if name == "DriverInfoboxOrchestrator":
        from scrapers.orchestration.driver_infobox_orchestrator import (
            DriverInfoboxOrchestrator,
        )

        return DriverInfoboxOrchestrator
    if name == "ConstructorInfoboxOrchestrator":
        from scrapers.orchestration.constructor_infobox_orchestrator import (
            ConstructorInfoboxOrchestrator,
        )

        return ConstructorInfoboxOrchestrator
    if name == "CircuitInfoboxExtractionService":
        from scrapers.orchestration.circuit_orchestrator import (
            CircuitInfoboxOrchestrator,
        )

        return CircuitInfoboxOrchestrator
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
