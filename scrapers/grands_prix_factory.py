"""Canonical factory module for grands prix domain."""

from dataclasses import dataclass

from scrapers.list_scraper_grands_prix import GrandsPrixListScraper


@dataclass(frozen=True)
class GrandsPrixFactory:
    """Factory for canonical grands prix scraper classes."""

    def build_list_scraper(self) -> type[GrandsPrixListScraper]:
        return GrandsPrixListScraper

    def build_detail_scraper(self) -> type[GrandsPrixDetailScraper]:
        return GrandsPrixDetailScraper


__all__ = ["GrandsPrixFactory"]
