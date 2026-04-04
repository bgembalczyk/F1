from scrapers.base.table.columns.types import AutoColumn
from scrapers.base.table.columns.types import IntColumn
from scrapers.base.table.columns.types import LinksListColumn
from scrapers.base.table.columns.types import SeasonsColumn
from scrapers.base.table.columns.types import SkipColumn
from scrapers.base.table.dsl.column import ColumnSpec
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.circuits.columns.circuit_name_status import CircuitNameStatusColumn
from scrapers.circuits.columns.last_length_used import LastLengthUsedColumn
from scrapers.circuits.constants import CIRCUIT_COUNTRY_HEADER
from scrapers.circuits.constants import CIRCUIT_DIRECTION_HEADER
from scrapers.circuits.constants import CIRCUIT_GRANDS_PRIX_HEADER
from scrapers.circuits.constants import CIRCUIT_GRANDS_PRIX_HELD_HEADER
from scrapers.circuits.constants import CIRCUIT_LAST_LENGTH_USED_HEADER
from scrapers.circuits.constants import CIRCUIT_LOCATION_HEADER
from scrapers.circuits.constants import CIRCUIT_MAP_HEADER
from scrapers.circuits.constants import CIRCUIT_NAME_HEADER
from scrapers.circuits.constants import CIRCUIT_SEASONS_HEADER
from scrapers.circuits.constants import CIRCUIT_TURNS_HEADER
from scrapers.circuits.constants import CIRCUIT_TYPE_HEADER
from scrapers.wiki.parsers.elements.wiki_table.base import WikiTableBaseParser


class CircuitsListTableParser(WikiTableBaseParser):
    """Specialized wikitable parser for the circuits list table."""

    table_type = "circuits_list"
    missing_columns_policy = "require_core_circuit_columns"
    extra_columns_policy = "ignore"

    _required_headers = frozenset({"Circuit", "Type", "Location", "Country"})
    _column_mapping = {
        "Circuit": "circuit",
        "Type": "type",
        "Location": "location",
        "Country": "country",
    }

    def matches(self, headers: list[str], _table_data: dict[str, object]) -> bool:
        return self._required_headers.issubset(set(headers))

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {
            header: self._column_mapping[header]
            for header in headers
            if header in self._column_mapping
        }


TABLE_SCHEMA = TableSchemaDSL(
    columns=[
        ColumnSpec(CIRCUIT_NAME_HEADER, "circuit", CircuitNameStatusColumn()),
        ColumnSpec(CIRCUIT_MAP_HEADER, "map", SkipColumn()),
        ColumnSpec(CIRCUIT_TYPE_HEADER, "type", AutoColumn()),
        ColumnSpec(CIRCUIT_DIRECTION_HEADER, "direction", AutoColumn()),
        ColumnSpec(CIRCUIT_LOCATION_HEADER, "location", AutoColumn()),
        ColumnSpec(CIRCUIT_COUNTRY_HEADER, "country", AutoColumn()),
        ColumnSpec(
            CIRCUIT_LAST_LENGTH_USED_HEADER,
            "last_length_used_km",
            LastLengthUsedColumn(),
        ),
        ColumnSpec(CIRCUIT_TURNS_HEADER, "turns", IntColumn()),
        ColumnSpec(CIRCUIT_GRANDS_PRIX_HEADER, "grands_prix", LinksListColumn()),
        ColumnSpec(CIRCUIT_SEASONS_HEADER, "seasons", SeasonsColumn()),
        ColumnSpec(
            CIRCUIT_GRANDS_PRIX_HELD_HEADER,
            "grands_prix_held",
            IntColumn(),
        ),
    ],
)
