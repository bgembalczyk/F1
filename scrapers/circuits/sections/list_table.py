from scrapers.base.table.columns import types as col
from scrapers.base.table.dsl.column import ColumnSpec
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.circuits.columns.circuit_name_status import CircuitNameStatusColumn
from scrapers.circuits.columns.last_length_used import LastLengthUsedColumn
from scrapers.circuits import constants
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
        ColumnSpec(constants.CIRCUIT_NAME_HEADER, "circuit", CircuitNameStatusColumn()),
        ColumnSpec(constants.CIRCUIT_MAP_HEADER, "map", col.SkipColumn()),
        ColumnSpec(constants.CIRCUIT_TYPE_HEADER, "type", col.AutoColumn()),
        ColumnSpec(constants.CIRCUIT_DIRECTION_HEADER, "direction", col.AutoColumn()),
        ColumnSpec(constants.CIRCUIT_LOCATION_HEADER, "location", col.AutoColumn()),
        ColumnSpec(constants.CIRCUIT_COUNTRY_HEADER, "country", col.AutoColumn()),
        ColumnSpec(
            constants.CIRCUIT_LAST_LENGTH_USED_HEADER,
            "last_length_used_km",
            LastLengthUsedColumn(),
        ),
        ColumnSpec(constants.CIRCUIT_TURNS_HEADER, "turns", col.IntColumn()),
        ColumnSpec(constants.CIRCUIT_GRANDS_PRIX_HEADER, "grands_prix", col.LinksListColumn()),
        ColumnSpec(constants.CIRCUIT_SEASONS_HEADER, "seasons", col.SeasonsColumn()),
        ColumnSpec(
            constants.CIRCUIT_GRANDS_PRIX_HELD_HEADER,
            "grands_prix_held",
            col.IntColumn(),
        ),
    ],
)
