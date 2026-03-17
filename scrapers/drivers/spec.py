from scrapers.base.table.domain_scraper_spec import DomainScraperSpec
from scrapers.drivers.validator import DriversRecordValidator

DRIVERS_LIST_SPEC = DomainScraperSpec(
    domain="drivers",
    base_url="https://en.wikipedia.org/wiki/List_of_Formula_One_drivers",
    options_profile="strict_seed",
    default_validator=DriversRecordValidator(),
    parser_section="Drivers",
)


def build_drivers_list_config(*, expected_headers, schema, record_factory):
    return DRIVERS_LIST_SPEC.make_config(
        section_id="Drivers",
        expected_headers=expected_headers,
        schema=schema,
        record_factory=record_factory,
    )
