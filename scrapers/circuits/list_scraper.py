from pathlib import Path

from models.validation.circuit import Circuit
from scrapers.base.helpers.runner import run_and_export
from scrapers.base.records import ExportRecord
from scrapers.base.run_config import RunConfig
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.scraper import F1TableScraper
from scrapers.base.validation import RecordValidator


class CircuitsListValidator(RecordValidator):
    def validate(self, record: ExportRecord) -> list[str]:
        errors: list[str] = []
        errors.extend(
            self.require_keys(
                record,
                ["circuit", "circuit_status", "country", "seasons"],
            )
        )
        errors.extend(self.require_type(record, "circuit", dict))
        errors.extend(self.require_type(record, "circuit_status", str))
        errors.extend(self.require_type(record, "country", (str, dict)))
        errors.extend(self.require_type(record, "seasons", list))
        errors.extend(self.require_type(record, "grands_prix", list, allow_none=True))

        circuit = record.get("circuit")
        if isinstance(circuit, dict):
            errors.extend(self.require_link_dict(circuit, "circuit"))

        grands_prix = record.get("grands_prix")
        if isinstance(grands_prix, list):
            errors.extend(self.require_link_list(grands_prix, "grands_prix"))

        return errors


class CircuitsListScraper(F1TableScraper):
    """
    Lista torów F1:
    https://en.wikipedia.org/wiki/List_of_Formula_One_circuits
    (duża tabela 'Circuits')
    """

    default_validator = CircuitsListValidator()

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
    )


if __name__ == "__main__":
    run_and_export(
        CircuitsListScraper,
        "circuits/f1_circuits.json",
        "circuits/f1_circuits.csv",
        run_config=RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
        ),
    )
from scrapers.circuits.columns.circuit_name_status import CircuitNameStatusColumn
from scrapers.circuits.columns.last_length_used import LastLengthUsedColumn
