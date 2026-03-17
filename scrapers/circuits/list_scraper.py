"""DEPRECATED ENTRYPOINT: use scrapers.circuits.entrypoint.run_list_scraper."""

from models.records.factories import build_circuit_record
from models.validation.circuit import Circuit
from scrapers.base.mixins.section_table_parse import DeclarativeSectionTableParseMixin
from scrapers.base.options import ScraperOptions
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper
from scrapers.circuits.constants import CIRCUITS_EXPECTED_HEADERS
from scrapers.circuits.schemas import build_circuits_schema
from scrapers.circuits.sections import CircuitsListSectionParser
from scrapers.circuits.spec import CIRCUITS_LIST_SPEC
from scrapers.circuits.spec import build_circuits_list_config


class CircuitsListScraper(DeclarativeSectionTableParseMixin, F1TableScraper):
    default_validator = CIRCUITS_LIST_SPEC.default_validator
    options_domain = CIRCUITS_LIST_SPEC.domain
    options_profile = CIRCUITS_LIST_SPEC.options_profile

    CONFIG = build_circuits_list_config(
        expected_headers=CIRCUITS_EXPECTED_HEADERS,
        model_class=Circuit,
        schema=build_circuits_schema(),
        record_factory=build_circuit_record,
    )

    def __init__(self, *, options: ScraperOptions | None = None, config: ScraperConfig | None = None) -> None:
        super().__init__(options=options, config=config)

    domain = "circuits"
    section_label = "Circuits"
    section_parser_class = CircuitsListSectionParser


if __name__ == "__main__":
    from scrapers.base.cli_entrypoint import build_deprecated_module_main
    from scrapers.circuits.entrypoint import run_list_scraper

    build_deprecated_module_main(
        target=run_list_scraper,
        deprecation_message=(
            "scrapers.circuits.list_scraper is deprecated; use "
            "scrapers.circuits.entrypoint.run_list_scraper."
        ),
    )()
