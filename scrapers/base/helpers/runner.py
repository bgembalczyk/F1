from pathlib import Path
from typing import Type

from scrapers.base.run_config import RunConfig
from scrapers.base.ABC import F1Scraper
from scrapers.base.runner import ScraperRunner


def run_and_export(
    scraper_cls: Type[F1Scraper],
    json_rel: str | Path,
    csv_rel: str | Path | None = None,
    *,
    run_config: RunConfig,
    supports_urls: bool = True,
) -> None:
    """
    Uruchamia scraper, a następnie zapisuje dane do JSON oraz CSV.

    - bezpiecznie przekazuje include_urls tylko jeśli ma sens,
    - tworzy katalogi dla ścieżek wyjściowych,
    - wypisuje liczbę pobranych rekordów,
    - eksport obsługuje ScrapeResult.
    """
    runner = ScraperRunner(run_config, supports_urls=supports_urls)
    runner.run_and_export(scraper_cls, json_rel, csv_rel)
