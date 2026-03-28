from scrapers.base.table.columns.types import AutoColumn
from scrapers.base.table.columns.types import IntColumn
from scrapers.base.table.columns.types import LinksListColumn
from scrapers.base.table.columns.types import SkipColumn
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.circuits.columns.circuit_name_status import CircuitNameStatusColumn
from scrapers.circuits.columns.last_length_used import LastLengthUsedColumn
from scrapers.circuits.columns.seasons import SeasonsColumn
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


def build_circuits_schema() -> TableSchemaDSL:
    return TableSchemaDSL(
        columns=[
            column(CIRCUIT_NAME_HEADER, "circuit", CircuitNameStatusColumn()),
            column(CIRCUIT_MAP_HEADER, "map", SkipColumn()),
            column(CIRCUIT_TYPE_HEADER, "type", AutoColumn()),
            column(CIRCUIT_DIRECTION_HEADER, "direction", AutoColumn()),
            column(CIRCUIT_LOCATION_HEADER, "location", AutoColumn()),
            column(CIRCUIT_COUNTRY_HEADER, "country", AutoColumn()),
            column(
                CIRCUIT_LAST_LENGTH_USED_HEADER,
                "last_length_used_km",
                LastLengthUsedColumn(),
            ),
            column(CIRCUIT_TURNS_HEADER, "turns", IntColumn()),
            column(CIRCUIT_GRANDS_PRIX_HEADER, "grands_prix", LinksListColumn()),
            column(CIRCUIT_SEASONS_HEADER, "seasons", SeasonsColumn()),
            column(
                CIRCUIT_GRANDS_PRIX_HELD_HEADER,
                "grands_prix_held",
                IntColumn(),
            ),
        ],
    )
