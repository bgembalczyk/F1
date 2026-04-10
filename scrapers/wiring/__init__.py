"""Runtime wiring, composition roots, and factories for scrapers."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scrapers.wiring.factory import ScraperFactory
    from scrapers.wiring.runtime.factory import ScraperRuntimeFactory

__all__ = ["ScraperFactory", "ScraperRuntimeFactory"]


def __getattr__(name: str):
    if name == "ScraperFactory":
        from scrapers.wiring.factory import ScraperFactory as _ScraperFactory

        return _ScraperFactory
    if name == "ScraperRuntimeFactory":
        from scrapers.wiring.runtime.factory import (
            ScraperRuntimeFactory as _ScraperRuntimeFactory,
        )

        return _ScraperRuntimeFactory
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
