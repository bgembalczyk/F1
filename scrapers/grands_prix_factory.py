"""Canonical factory module for grands prix domain."""

from dataclasses import dataclass

from scrapers.grands_prix.single_scraper import GrandsPrixDetailScraper
from scrapers.grands_prix.list_scraper import GrandsPrixListScraper


@dataclass(frozen=True)
class GrandsPrixFactory:
    """Factory for canonical grands prix scraper classes."""

    def build_list_scraper(self) -> type[GrandsPrixListScraper]:
        return GrandsPrixListScraper

    def build_detail_scraper(self) -> type[GrandsPrixDetailScraper]:
        return GrandsPrixDetailScraper


__all__ = ["GrandsPrixFactory"]
