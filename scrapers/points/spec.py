from scrapers.base.table.domain_scraper_spec import DomainScraperSpec
from scrapers.points.base_points_scraper import BasePointsScraper

POINTS_LIST_SPEC = DomainScraperSpec(
    domain="points",
    base_url=BasePointsScraper.BASE_URL,
    options_profile="soft_seed",
)


def build_points_list_config(*, section_id, expected_headers, schema, record_factory):
    return POINTS_LIST_SPEC.make_config(
        section_id=section_id,
        expected_headers=expected_headers,
        schema=schema,
        record_factory=record_factory,
    )
