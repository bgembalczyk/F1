from scrapers.base.table.domain_scraper_spec import DomainScraperSpec

ENGINES_LIST_SPEC = DomainScraperSpec(
    domain="engines",
    base_url="https://en.wikipedia.org/wiki/List_of_Formula_One_engine_manufacturers",
    options_profile="soft_seed",
    parser_section="engine_tables",
)


def build_engine_manufacturers_config(*, expected_headers, schema, record_factory, model_class):
    return ENGINES_LIST_SPEC.make_config(
        section_id="Engine_manufacturers",
        expected_headers=expected_headers,
        schema=schema,
        record_factory=record_factory,
        model_class=model_class,
    )


def build_engine_regulation_config(*, expected_headers, schema, record_factory, model_class):
    return ENGINES_LIST_SPEC.make_config(
        section_id="Engine_regulation_progression_by_era",
        expected_headers=expected_headers,
        schema=schema,
        record_factory=record_factory,
        model_class=model_class,
    )


def build_engine_restrictions_config(*, expected_headers, schema, record_factory):
    return ENGINES_LIST_SPEC.make_config(
        section_id="Engine",
        expected_headers=expected_headers,
        schema=schema,
        record_factory=record_factory,
    )
