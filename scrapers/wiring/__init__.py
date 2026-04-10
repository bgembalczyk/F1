"""Runtime wiring, composition roots, and factories for scrapers."""

from scrapers.wiring.factory import ScraperFactory
from scrapers.wiring.runtime.factory import ScraperRuntimeFactory

__all__ = ["ScraperFactory", "ScraperRuntimeFactory"]
