from scrapers.base.table.domain_scraper_spec import DomainScraperSpec
from scrapers.grands_prix.validator import GrandsPrixRecordValidator

GRANDS_PRIX_LIST_SPEC = DomainScraperSpec(
    domain="grands_prix",
    base_url="https://en.wikipedia.org/wiki/List_of_Formula_One_Grands_Prix",
    options_profile="soft_seed",
    default_validator=GrandsPrixRecordValidator(),
    parser_section="By_race_title",
)


def build_grands_prix_list_config(*, expected_headers, schema, record_factory):
    return GRANDS_PRIX_LIST_SPEC.make_config(
        section_id="By_race_title",
        expected_headers=expected_headers,
        schema=schema,
        record_factory=record_factory,
    )
