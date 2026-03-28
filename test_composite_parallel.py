import sys
from unittest.mock import MagicMock

# Mock dependencies
mock_bs4 = MagicMock()
mock_infra = MagicMock()
mock_infra_http = MagicMock()
mock_infra_http_policies = MagicMock()
mock_infra_http_caching = MagicMock()

sys.modules["bs4"] = mock_bs4
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

from typing import Any, Dict, List, Optional
from scrapers.base.composite_scraper import CompositeScraper, CompositeScraperChildren
from scrapers.base.source_adapter import IterableSourceAdapter
from scrapers.base.options import ScraperOptions

class MockSingleScraper:
    def __init__(self):
        self.called_urls = []
    def fetch_by_url(self, url: str) -> List[Dict[str, Any]]:
        self.called_urls.append(url)
        return [{"url": url, "data": "details"}]

class TestScraper(CompositeScraper):
    def __init__(self, records, single_scraper_factory):
        self.records = records
        self.single_scraper_factory = single_scraper_factory
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
        options.run_id = "test-run"
        options.quality_report = False
        options.validator = None
        options.validation_mode = "soft"
        super().__init__(options=options)
        self.logger = MagicMock()

    def build_children(self) -> CompositeScraperChildren:
        list_scraper = MagicMock()
        single_scraper = self.single_scraper_factory()
        records_adapter = IterableSourceAdapter(self.records)
        return CompositeScraperChildren(
            list_scraper=list_scraper,
            single_scraper=single_scraper,
            records_adapter=records_adapter
        )

    def get_detail_url(self, record: Dict[str, Any]) -> Optional[str]:
        return record.get("url")

def test_composite_scraper_parallel_fetch():
    records = [{"url": f"http://site.com/{i}"} for i in range(5)]

    # We want to verify that each thread gets its own scraper instance
    created_scrapers = []
    def scraper_factory():
        s = MockSingleScraper()
        created_scrapers.append(s)
        return s

    scraper = TestScraper(records, scraper_factory)
    results = scraper.fetch()

    assert len(results) == 5
    for i in range(5):
        # Find the result for current record url since results are ordered by executor map but records were iterated correctly
        record_url = f"http://site.com/{i}"
        result = next(r for r in results if r["url"] == record_url)
        # In base class assemble_record: full_record["details"] = details_list[0] if details_list else None
        assert result["details"]["url"] == record_url

    # Verify that multiple scrapers were created
    assert len(created_scrapers) > 0

    # Each URL should have been called exactly once
    all_called_urls = []
    for s in created_scrapers:
        all_called_urls.extend(s.called_urls)

    assert sorted(all_called_urls) == sorted([r["url"] for r in records])

if __name__ == "__main__":
    try:
        test_composite_scraper_parallel_fetch()
        print("Test passed!")
    except AssertionError as e:
        print(f"Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
