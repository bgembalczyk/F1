from __future__ import annotations

"""Base scraper and shared factory for Indianapolis 500 only lists."""

from dataclasses import dataclass

from scrapers.base.list.scraper import F1ListScraper


@dataclass(frozen=True, slots=True)
class IndianapolisOnlyListConfig:
    """Declarative configuration for Indianapolis 500 only list scrapers."""

    url: str
    record_key: str
    url_key: str
    domain_name: str | None = None
    record_type: str | None = None


def build_indianapolis_only_list_scraper(
    *,
    class_name: str,
    config: IndianapolisOnlyListConfig,
) -> type["IndianapolisOnlyListScraper"]:
    """Build a configured Indianapolis-only list scraper class.

    Domain modules should only provide the source URL and output field names,
    while this factory handles the shared class structure.
    """

    namespace = {
        "__doc__": (
            f"Indianapolis 500 only list scraper for {config.domain_name or class_name}."
        ),
        "url": config.url,
        "record_key": config.record_key,
        "url_key": config.url_key,
        "domain_name": config.domain_name,
        "record_type": config.record_type,
        "CONFIG": config,
    }
    return type(class_name, (IndianapolisOnlyListScraper,), namespace)


class IndianapolisOnlyListScraper(F1ListScraper):
    """Base class for Indianapolis 500 only list scrapers."""

    section_id = "Indianapolis_500_only"
    domain_name: str | None = None
    record_type: str | None = None
    CONFIG: IndianapolisOnlyListConfig | None = None
