from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scrapers.runners.pipeline_runner import ScraperPipelineRunner
    from scrapers.runners.scraper_runner import ScraperRunner

__all__ = ["ScraperPipelineRunner", "ScraperRunner"]


def __getattr__(name: str):
    if name == "ScraperPipelineRunner":
        from scrapers.runners.pipeline_runner import (
            ScraperPipelineRunner as _ScraperPipelineRunner,
        )

        return _ScraperPipelineRunner
    if name == "ScraperRunner":
        from scrapers.runners.scraper_runner import ScraperRunner as _ScraperRunner

        return _ScraperRunner
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
