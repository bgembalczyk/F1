from pathlib import Path

from models.records.factories import build_circuit_record
from models.validation.circuit import Circuit
from scrapers.base.helpers.config_factory import ScraperCommonConfig
from scrapers.base.helpers.config_factory import build_table_config
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.options import ScraperOptions
from scrapers.base.run_config import RunConfig
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper
from scrapers.circuits.constants import CIRCUITS_EXPECTED_HEADERS
from scrapers.circuits.schemas import build_circuits_schema
from scrapers.circuits.validator import CircuitsRecordValidator


class CircuitsListScraper(F1TableScraper):
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


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--quality-report",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Zapisz raport jakości do debug_dir/quality_report.json.",
    )
    parser.add_argument(
        "--error-report",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Zapisz raporty błędów do debug_dir/errors.jsonl.",
    )
    args = parser.parse_args()
    run_and_export(
        CircuitsListScraper,
        "circuits/f1_circuits.json",
        "circuits/f1_circuits.csv",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
            debug_dir=Path("../../data/debug"),
            quality_report=args.quality_report,
            error_report=args.error_report,
        ),
    )
