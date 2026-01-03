from pathlib import Path

from models.records.factories import build_circuit_record
from models.validation.circuit import Circuit
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.options import ScraperOptions
from scrapers.base.run_config import RunConfig
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper
from scrapers.base.table.schema import TableSchemaBuilder
from scrapers.circuits.columns.circuit_name_status import CircuitNameStatusColumn
from scrapers.circuits.columns.last_length_used import LastLengthUsedColumn
from scrapers.circuits.validation import CircuitsRecordValidator


def _build_circuits_schema() -> TableSchemaBuilder:
    return (
        TableSchemaBuilder()
        .map("Circuit", "circuit", CircuitNameStatusColumn())
        .map("Map", "map", SkipColumn())
        .map("Type", "type", AutoColumn())
        .map("Direction", "direction", AutoColumn())
        .map("Location", "location", AutoColumn())
        .map("Country", "country", AutoColumn())
        .map("Last length used", "last_length_used", LastLengthUsedColumn())
        .map("Turns", "turns", IntColumn())
        .map("Grands Prix", "grands_prix", LinksListColumn())
        .map("Season(s)", "seasons", SeasonsColumn())
        .map("Grands Prix held", "grands_prix_held", IntColumn())
    )


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
        expected_headers=[
            "Circuit",
            "Type",
            "Location",
            "Country",
        ],
        model_class=Circuit,
        schema=_build_circuits_schema(),
        record_factory=build_circuit_record,
    )

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        config: ScraperConfig | None = None,
    ) -> None:
        options = options or ScraperOptions()
        options.validation_mode = "soft"
        super().__init__(options=options, config=config)


if __name__ == "__main__":
    run_and_export(
        CircuitsListScraper,
        "circuits/f1_circuits.json",
        "circuits/f1_circuits.csv",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
            debug_dir=Path("../../data/debug"),
        ),
    )
