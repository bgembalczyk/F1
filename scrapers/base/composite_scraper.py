from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from scrapers.base.ABC import F1Scraper
from scrapers.base.source_adapter import IterableSourceAdapter


@dataclass(frozen=True)
class CompositeScraperChildren:
    list_scraper: F1Scraper
    single_scraper: Any
    records_adapter: IterableSourceAdapter[Dict[str, Any]]


class CompositeScraper(F1Scraper):
    def __init__(self, *, options) -> None:
        super().__init__(options=options)
        self.options = options
        children = self.build_children()
        self.list_scraper = children.list_scraper
        self.single_scraper = children.single_scraper
        self.records_adapter = children.records_adapter

    def build_children(self) -> CompositeScraperChildren:
        raise NotImplementedError("CompositeScraper requires build_children().")

    def get_detail_url(self, record: Dict[str, Any]) -> Optional[str]:
        return None

    def assemble_record(
        self,
        record: Dict[str, Any],
        details: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        full_record = dict(record)
        full_record["details"] = details
        return full_record

    def fetch(self) -> List[Dict[str, Any]]:
        records = self.records_adapter.get()
        complete: List[Dict[str, Any]] = []

        for record in records:
            if not isinstance(record, dict):
                raise TypeError(
                    f"{self.list_scraper.__class__.__name__} musi zwracać dict, "
                    f"otrzymano: {type(record).__name__}"
                )

            detail_url = self.get_detail_url(record)
            details: Optional[Dict[str, Any]] = None

            if detail_url:
                try:
                    details_list = self.single_scraper.fetch_by_url(detail_url)
                    details = details_list[0] if details_list else None
                except Exception:
                    self.logger.exception(
                        "Nie udało się pobrać szczegółów rekordu (url=%s).",
                        detail_url,
                    )

            complete.append(self.assemble_record(record, details))

        self._data = complete
        return self._data
