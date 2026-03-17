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
from scrapers.circuits.validator import CircuitsRecordValidator


class CircuitsListScraper(DeclarativeSectionTableParseMixin, F1TableScraper):
    """
    Lista torów F1:
    https://en.wikipedia.org/wiki/List_of_Formula_One_circuits
    (duża tabela 'Circuits')
    """

    default_validator = CircuitsRecordValidator()
    options_domain = "circuits"
    options_profile = "soft_seed"

    CONFIG = ScraperConfig(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_circuits",
        section_id="Circuits",
        expected_headers=CIRCUITS_EXPECTED_HEADERS,
        model_class=Circuit,
        schema=build_circuits_schema(),
        record_factory=build_circuit_record,
    )

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        config: ScraperConfig | None = None,
    ) -> None:
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
