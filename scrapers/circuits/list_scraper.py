"""DEPRECATED ENTRYPOINT: use scrapers.circuits.entrypoint.run_list_scraper."""

from pathlib import Path

from models.records.factories import build_circuit_record
from models.validation.circuit import Circuit
from scrapers.base.helpers.config_factory import ScraperCommonConfig
from scrapers.base.helpers.config_factory import build_table_config
from scrapers.base.mixins.section_table_parse import SectionTableParseMixin
from scrapers.base.options import ScraperOptions
from scrapers.base.run_config import RunConfig
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper
from scrapers.circuits.constants import CIRCUITS_EXPECTED_HEADERS
from scrapers.circuits.schemas import build_circuits_schema
from scrapers.circuits.sections import CircuitsListSectionParser
from scrapers.circuits.validator import CircuitsRecordValidator


class CircuitsListScraper(SectionTableParseMixin, F1TableScraper):
    """
    Lista torów F1:
    https://en.wikipedia.org/wiki/List_of_Formula_One_circuits
    (duża tabela 'Circuits')
    """

    default_validator = CircuitsRecordValidator()

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
        options = build_table_config(
            options,
            config=ScraperCommonConfig(
                include_urls=True,
                normalize_empty_values=False,
                validation_mode="soft",
            ),
        )
        super().__init__(options=options, config=config)

    def _parse_soup(self, soup):
        return self.parse_section_or_fallback(
            soup,
            domain="circuits",
            section_label="Circuits",
            parser_factory=lambda: CircuitsListSectionParser(
                config=self.config,
                include_urls=self.include_urls,
                normalize_empty_values=self.normalize_empty_values,
            ),
        )


if __name__ == "__main__":
    from scrapers.base.cli_entrypoint import run_cli_entrypoint
    from scrapers.circuits.entrypoint import run_list_scraper

    run_cli_entrypoint(
        target=run_list_scraper,
        base_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
            debug_dir=Path("../../data/debug"),
        ),
        quality_report_default=True,
        error_report_default=False,
        deprecation_message=(
            "scrapers.circuits.list_scraper is deprecated; use "
            "scrapers.circuits.entrypoint.run_list_scraper."
        ),
    )
