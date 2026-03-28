import threading
from concurrent.futures import ThreadPoolExecutor
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
    def __init__(
        self,
        *,
        options,
        max_workers: int = 10,
    ) -> None:
        super().__init__(options=options)
        self.options = options
        self.max_workers = max_workers
        children = self.build_children()
        self.list_scraper = children.list_scraper
        self.single_scraper = children.single_scraper
        self.records_adapter = children.records_adapter
        self._thread_local = threading.local()

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
        records = list(self.records_adapter.get())

        for record in records:
            if not isinstance(record, dict):
                raise TypeError(
                    f"{self.list_scraper.__class__.__name__} musi zwracać dict, "
                    f"otrzymano: {type(record).__name__}"
                )

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(executor.map(self._fetch_record_details, records))

        self._data = results
        return self._data

    def _fetch_record_details(self, record: Dict[str, Any]) -> Dict[str, Any]:
        detail_url = self.get_detail_url(record)
        details: Optional[Dict[str, Any]] = None

        if detail_url:
            try:
                # Use thread-local single_scraper to ensure thread-safety
                # if the scraper or its dependencies are not thread-safe.
                # Many scrapers in this project store state (like self.url) during fetch.
                scraper = self._get_thread_local_scraper()
                details_list = scraper.fetch_by_url(detail_url)
                details = details_list[0] if details_list else None
            except Exception:
                self.logger.exception(
                    "Nie udało się pobrać szczegółów rekordu (url=%s).",
                    detail_url,
                )

        return self.assemble_record(record, details)

    def _get_thread_local_scraper(self) -> Any:
        if not hasattr(self._thread_local, "single_scraper"):
            # Re-building children per thread might be expensive,
            # but it ensures each thread has its own isolated scraper instance.
            # Alternatively, we could deepcopy the original single_scraper.
            children = self.build_children()
            self._thread_local.single_scraper = children.single_scraper
        return self._thread_local.single_scraper
