"""DEPRECATED ENTRYPOINT: use scrapers.circuits.entrypoint.run_list_scraper."""

from models.validation.circuit import Circuit
from scrapers.adapters.factories.dataclass import RECORD_FACTORIES
from scrapers.circuits_constants import CIRCUITS_EXPECTED_HEADERS
from scrapers.config_table import build_scraper_config
from scrapers.mixins.section_table_parse.declarative import DeclarativeSectionTableParseMixin
from scrapers.parsers.section.list.circuits import CircuitsListSectionParser
from scrapers.parsers.table.wiki.circuit_list import TABLE_SCHEMA
from scrapers.seed_list_scraper_table import SeedListTableScraper
from scrapers.source_catalog import CIRCUITS_LIST


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
        schema=TABLE_SCHEMA,
        record_factory=RECORD_FACTORIES.builders("circuit"),
    )

    section_label = "Circuits"
    section_parser_class = CircuitsListSectionParser


__all__ = ["CircuitsListScraper"]
