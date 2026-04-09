"""Base mixin and shared factory for Indianapolis 500 only lists."""

from __future__ import annotations

from dataclasses import dataclass

from scrapers.list.base import ListScraper
from scrapers.list.indianapolis_only.base import IndianapolisOnlyListScraper
from scrapers.list.indianapolis_only.config import IndianapolisOnlyListConfig


def build_indianapolis_only_list_scraper(
    *,
    class_name: str,
    config: IndianapolisOnlyListConfig,
) -> type[ListScraper]:
    """Build a configured Indianapolis-only list scraper class.

    Domain modules should only provide the source URL and output field names,
    while this factory handles the shared class structure.
    """

    namespace = {
        "__doc__": f"Indianapolis 500 only list scraper for "
        f"{config.domain_name or class_name}.",
        "url": config.url,
        "record_key": config.record_key,
        "url_key": config.url_key,
        "domain_name": config.domain_name,
        "record_type": config.record_type,
        "CONFIG": config,
    }
    return type(
        class_name,
        (IndianapolisOnlyListScraper,),
        namespace,
    )


