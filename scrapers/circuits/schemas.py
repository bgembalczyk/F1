from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.dsl import TableSchemaDSL, column
from scrapers.circuits.columns.circuit_name_status import CircuitNameStatusColumn
from scrapers.circuits.columns.last_length_used import LastLengthUsedColumn
from scrapers.circuits.constants import CIRCUIT_HEADER
from scrapers.circuits.constants import COUNTRY_HEADER
from scrapers.circuits.constants import DIRECTION_HEADER
from scrapers.circuits.constants import GRANDS_PRIX_HEADER
from scrapers.circuits.constants import GRANDS_PRIX_HELD_HEADER
from scrapers.circuits.constants import LAST_LENGTH_USED_HEADER
from scrapers.circuits.constants import LOCATION_HEADER
from scrapers.circuits.constants import MAP_HEADER
from scrapers.circuits.constants import SEASONS_HEADER
from scrapers.circuits.constants import TURNS_HEADER
from scrapers.circuits.constants import TYPE_HEADER


def build_circuits_schema() -> TableSchemaDSL:
    return TableSchemaDSL(
        columns=[
            column(CIRCUIT_HEADER, "circuit", CircuitNameStatusColumn()),
            column(MAP_HEADER, "map", SkipColumn()),
            column(TYPE_HEADER, "type", AutoColumn()),
            column(DIRECTION_HEADER, "direction", AutoColumn()),
            column(LOCATION_HEADER, "location", AutoColumn()),
            column(COUNTRY_HEADER, "country", AutoColumn()),
            column(
                LAST_LENGTH_USED_HEADER,
                "last_length_used_km",
                LastLengthUsedColumn(),
            ),
            column(TURNS_HEADER, "turns", IntColumn()),
            column(GRANDS_PRIX_HEADER, "grands_prix", LinksListColumn()),
            column(SEASONS_HEADER, "seasons", SeasonsColumn()),
            column(GRANDS_PRIX_HELD_HEADER, "grands_prix_held", IntColumn()),
        ]
    )
