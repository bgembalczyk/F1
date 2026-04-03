"""DEPRECATED ENTRYPOINT: use scrapers.circuits.entrypoint.run_list_scraper."""

from models.validation.circuit import Circuit
from scrapers.base.factory.record_factory import RECORD_FACTORIES
from scrapers.base.mixins.section_table_parse import DeclarativeSectionTableParseMixin
from scrapers.base.source_catalog import CIRCUITS_LIST
from scrapers.base.table.config import build_scraper_config
from scrapers.base.table.seed_list_scraper import SeedListTableScraper
from scrapers.circuits.constants import CIRCUITS_EXPECTED_HEADERS
from scrapers.circuits.sections.list_section import CircuitsListSectionParser
from scrapers.circuits.sections.list_table import CircuitsListTableParser


class CircuitsListScraper(DeclarativeSectionTableParseMixin, SeedListTableScraper):
    domain = "circuits"

    """
    Lista torów F1:
    https://en.wikipedia.org/wiki/List_of_Formula_One_circuits
    (duża tabela 'Circuits')
    """

    CONFIG = build_scraper_config(
        url=CIRCUITS_LIST.base_url,
        section_id=CIRCUITS_LIST.section_id,
        expected_headers=CIRCUITS_EXPECTED_HEADERS,
        model_class=Circuit,
        schema=CircuitsListTableParser.build_schema(),
        record_factory=RECORD_FACTORIES.builders("circuit"),
    )

    section_label = "Circuits"
    section_parser_class = CircuitsListSectionParser
