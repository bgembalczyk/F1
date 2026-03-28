"""DEPRECATED ENTRYPOINT: use scrapers.circuits.entrypoint.run_list_scraper."""

from models.records.factories.build import RECORD_BUILDERS
from models.validation.circuit import Circuit
from scrapers.base.mixins.section_table_parse import DeclarativeSectionTableParseMixin
from scrapers.base.table.config import build_scraper_config
from scrapers.base.table.seed_list_scraper import SeedListTableScraper
from scrapers.circuits.constants import CIRCUITS_EXPECTED_HEADERS
from scrapers.circuits.schemas import build_circuits_schema
from scrapers.circuits.sections.list_section import CircuitsListSectionParser
from scrapers.circuits.validator import CircuitsRecordValidator


class CircuitsListScraper(DeclarativeSectionTableParseMixin, SeedListTableScraper):
    domain = "circuits"
    default_output_path = "raw/circuits/seeds/complete_circuits"
    legacy_output_path = "circuits/complete_circuits"

    """
    Lista torów F1:
    https://en.wikipedia.org/wiki/List_of_Formula_One_circuits
    (duża tabela 'Circuits')
    """

    default_validator = CircuitsRecordValidator()

    CONFIG = build_scraper_config(
        url="https://en.wikipedia.org/wiki/List_of_Formula_One_circuits",
        section_id="Circuits",
        expected_headers=CIRCUITS_EXPECTED_HEADERS,
        model_class=Circuit,
        schema=build_circuits_schema(),
        record_factory=RECORD_BUILDERS.circuit,
    )

    section_label = "Circuits"
    section_parser_class = CircuitsListSectionParser


if __name__ == "__main__":
    from scrapers.cli import run_current_legacy_wrapper

    run_current_legacy_wrapper()
