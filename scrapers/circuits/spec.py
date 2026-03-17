from scrapers.base.table.domain_scraper_spec import DomainScraperSpec
from scrapers.circuits.validator import CircuitsRecordValidator

CIRCUITS_LIST_SPEC = DomainScraperSpec(
    domain="circuits",
    base_url="https://en.wikipedia.org/wiki/List_of_Formula_One_circuits",
    options_profile="soft_seed",
    default_validator=CircuitsRecordValidator(),
    parser_section="Circuits",
)


def build_circuits_list_config(*, expected_headers, schema, record_factory, model_class):
    return CIRCUITS_LIST_SPEC.make_config(
        section_id="Circuits",
        expected_headers=expected_headers,
        schema=schema,
        record_factory=record_factory,
        model_class=model_class,
    )
