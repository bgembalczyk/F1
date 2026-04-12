from scrapers.circuits_constants import CIRCUIT_COUNTRY_HEADER
from scrapers.circuits_constants import CIRCUIT_DIRECTION_HEADER
from scrapers.circuits_constants import CIRCUIT_GRANDS_PRIX_HEADER
from scrapers.circuits_constants import CIRCUIT_GRANDS_PRIX_HELD_HEADER
from scrapers.circuits_constants import CIRCUIT_LAST_LENGTH_USED_HEADER
from scrapers.circuits_constants import CIRCUIT_LOCATION_HEADER
from scrapers.circuits_constants import CIRCUIT_MAP_HEADER
from scrapers.circuits_constants import CIRCUIT_NAME_HEADER
from scrapers.circuits_constants import CIRCUIT_SEASONS_HEADER
from scrapers.circuits_constants import CIRCUIT_TURNS_HEADER
from scrapers.circuits_constants import CIRCUIT_TYPE_HEADER
from scrapers.columns.factory import IntColumn
from scrapers.columns.spec import ColumnSpec
from scrapers.columns.types.auto import AutoColumn
from scrapers.columns.types.links_list import LinksListColumn
from scrapers.columns.types.multi.last_length_used import LastLengthUsedColumn
from scrapers.columns.types.multi.name_status_column import CircuitNameStatusColumn
from scrapers.columns.types.seasons import SeasonsColumn
from scrapers.columns.types.skip import SkipColumn
from scrapers.mappers.wiki_tables.base_mapper import MappedWikiTableMapper
from scrapers.table_schema_dsl import TableSchemaDSL


class CircuitsListTableMapper(MappedWikiTableMapper):
    """Specialized wikitable parser for the circuits list table."""

    table_type = "circuits_list"
    missing_columns_policy = "require_core_circuit_columns"
    extra_columns_policy = "ignore"

    required_header_groups = (
        frozenset({"Circuit"}),
        frozenset({"Type"}),
        frozenset({"Location"}),
        frozenset({"Country"}),
    )
    column_mapping = {
        "Circuit": "circuit",
        "Type": "type",
        "Location": "location",
        "Country": "country",
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
        ColumnSpec(
            CIRCUIT_GRANDS_PRIX_HEADER,
            "grands_prix",
            LinksListColumn(),
        ),
        ColumnSpec(CIRCUIT_SEASONS_HEADER, "seasons", SeasonsColumn()),
        ColumnSpec(
            CIRCUIT_GRANDS_PRIX_HELD_HEADER,
            "grands_prix_held",
            IntColumn(),
        ),
    ],
)
