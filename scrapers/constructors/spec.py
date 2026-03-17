from scrapers.base.table.domain_scraper_spec import DomainScraperSpec

CONSTRUCTORS_LIST_SPEC = DomainScraperSpec(
    domain="constructors",
    base_url="https://en.wikipedia.org/wiki/List_of_Formula_One_constructors",
    options_profile="soft_seed",
    parser_section="constructors_list",
)


def build_constructors_list_config(
    *,
    section_id: str,
    expected_headers,
    schema,
    record_factory,
):
    return CONSTRUCTORS_LIST_SPEC.make_config(
        section_id=section_id,
        expected_headers=expected_headers,
        schema=schema,
        record_factory=record_factory,
    )
