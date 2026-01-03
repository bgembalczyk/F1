from pathlib import Path

from models.records.factories import build_circuit_record
from models.validation.circuit import Circuit
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.options import ScraperOptions
from scrapers.base.run_config import RunConfig
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper
from scrapers.circuits.columns.circuit_name_status import CircuitNameStatusColumn
from scrapers.circuits.columns.last_length_used import LastLengthUsedColumn
from scrapers.circuits.validation import CircuitsRecordValidator


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
        column_map={
            "Circuit": "circuit",
            "Map": "map",
            "Type": "type",
            "Direction": "direction",
            "Location": "location",
            "Country": "country",
            "Last length used": "last_length_used",
            "Turns": "turns",
            "Grands Prix": "grands_prix",
            "Season(s)": "seasons",
            "Grands Prix held": "grands_prix_held",
        },
        columns={
            # proste kolumny
            "map": SkipColumn(),
            "seasons": SeasonsColumn(),
            "turns": IntColumn(),
            "grands_prix_held": IntColumn(),
            # Circuit → MultiColumn: circuit (url) + circuit_status (enum z raw_text)
            "circuit": CircuitNameStatusColumn(),
            # Last length used → MultiColumn: km + mi z jednego raw_text
            # Last length used → MultiColumn: km + mi z tego samego tekstu
            "last_length_used": LastLengthUsedColumn(),
            # Grands Prix → lista linków bez znaczników
            "grands_prix": LinksListColumn(),
            # alternatywnie: LinksListColumn() + mała modyfikacja tekstu w osobnej kolumnie
        },
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
