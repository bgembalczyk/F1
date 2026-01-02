import inspect
from pathlib import Path
from typing import Type

from scrapers.base.run_config import RunConfig
from scrapers.base.runner import ScraperRunner
from scrapers.base.scraper import F1Scraper


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def supports_param(cls: type, param_name: str) -> bool:
    """
    True jeśli __init__ klasy przyjmuje param o nazwie param_name
    albo ma **kwargs (wtedy też możemy bezpiecznie podać).
    """
    try:
        sig = inspect.signature(cls.__init__)
    except (TypeError, ValueError):
        return False

    params = sig.parameters
    if param_name in params:
        return True
    return any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values())


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
