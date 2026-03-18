"""DEPRECATED ENTRYPOINT: use scrapers.circuits.entrypoint.run_list_scraper."""

from models.records.factories.build import RECORD_BUILDERS
from models.validation.circuit import Circuit
from scrapers.base.mixins.section_table_parse import DeclarativeSectionTableParseMixin
from scrapers.base.options import ScraperOptions
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper
from scrapers.circuits.constants import CIRCUITS_EXPECTED_HEADERS
from scrapers.circuits.schemas import build_circuits_schema
from scrapers.circuits.sections.list_section import CircuitsListSectionParser
from scrapers.circuits.validator import CircuitsRecordValidator
from scrapers.wiki.component_metadata import ComponentMetadata


class CircuitsListScraper(DeclarativeSectionTableParseMixin, F1TableScraper):
    COMPONENT_METADATA = ComponentMetadata.build_layer_one_list_scraper(
        domain="circuits",
        default_output_path="raw/circuits/seeds/complete_circuits",
        legacy_output_path="circuits/complete_circuits",
    )

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
        record_factory=RECORD_BUILDERS.circuit,
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
    from scrapers.cli import run_current_legacy_wrapper

    run_current_legacy_wrapper()
