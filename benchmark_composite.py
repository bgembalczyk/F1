import sys
from unittest.mock import MagicMock

# Mock dependencies to bypass missing packages and circular imports
# Define mock modules first to avoid sub-module import errors
mock_infra = MagicMock()
mock_infra_http = MagicMock()
mock_infra_http_policies = MagicMock()
mock_infra_http_caching = MagicMock()

sys.modules["bs4"] = MagicMock()
sys.modules["infrastructure"] = mock_infra
sys.modules["infrastructure.http_client"] = mock_infra_http
sys.modules["infrastructure.http_client.interfaces"] = MagicMock()
sys.modules["infrastructure.http_client.interfaces.http_client_protocol"] = MagicMock()
sys.modules["infrastructure.http_client.clients"] = MagicMock()
sys.modules["infrastructure.http_client.clients.urllib_http"] = MagicMock()
sys.modules["infrastructure.http_client.config"] = MagicMock()
sys.modules["infrastructure.http_client.policies"] = mock_infra_http_policies
sys.modules["infrastructure.http_client.policies.defaults"] = MagicMock()
sys.modules["infrastructure.http_client.policies.http"] = MagicMock()
sys.modules["infrastructure.http_client.policies.response_cache"] = MagicMock()
sys.modules["infrastructure.http_client.caching"] = mock_infra_http_caching
sys.modules["infrastructure.http_client.caching.wiki"] = MagicMock()
sys.modules["infrastructure.http_client.caching.file"] = MagicMock()
sys.modules["validation"] = MagicMock()
sys.modules["validation.records"] = MagicMock()
sys.modules["pandas"] = MagicMock()

import time
from typing import Any, Dict, List, Optional
from scrapers.base.composite_scraper import CompositeScraper, CompositeScraperChildren
from scrapers.base.source_adapter import IterableSourceAdapter
from scrapers.base.options import ScraperOptions

class MockSingleScraper:
    def __init__(self, delay=0.1):
        self.delay = delay
    def fetch_by_url(self, url: str) -> List[Dict[str, Any]]:
        time.sleep(self.delay)
        return [{"url": url, "data": "some details"}]

class BenchmarkScraper(CompositeScraper):
    def __init__(self, num_records=10, delay=0.1):
        self.num_records = num_records
        self.delay = delay
        # Mock options
        options = MagicMock(spec=ScraperOptions)
        options.include_urls = True
        options.normalize_empty_values = False
        options.policy = None
        options.fetcher = None
        options.source_adapter = None
        options.parser = None
        options.exporter = None
        options.transformers = []
        options.post_processors = []
        options.debug_dir = None
        options.error_report = False
        options.run_id = "bench-run"
        options.quality_report = False
        options.validator = None
        options.validation_mode = "soft"

        super().__init__(options=options)
        self.logger = MagicMock()

    def build_children(self) -> CompositeScraperChildren:
        records = [{"id": i, "url": f"http://example.com/{i}"} for i in range(self.num_records)]
        list_scraper = MagicMock()
        single_scraper = MockSingleScraper(delay=self.delay)
        records_adapter = IterableSourceAdapter(records)
        return CompositeScraperChildren(
            list_scraper=list_scraper,
            single_scraper=single_scraper,
            records_adapter=records_adapter
        )

    def get_detail_url(self, record: Dict[str, Any]) -> Optional[str]:
        return record.get("url")

def run_benchmark():
    num_records = 20
    delay = 0.05
    scraper = BenchmarkScraper(num_records=num_records, delay=delay)

    print(f"Starting benchmark with {num_records} records and {delay}s delay per record...")
    start_time = time.time()
    scraper.fetch()
    end_time = time.time()

    duration = end_time - start_time
    print(f"Fetched {num_records} records in {duration:.4f} seconds")
    print(f"Theoretical minimum time (serial): {num_records * delay:.4f}s")

if __name__ == "__main__":
    run_benchmark()
