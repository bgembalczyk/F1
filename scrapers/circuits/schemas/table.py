from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.skip import SkipColumn
from scrapers.base.table.schema import TableSchemaBuilder
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


def build_circuits_schema() -> TableSchemaBuilder:
    return (
        TableSchemaBuilder()
        .map(CIRCUIT_HEADER, "circuit", CircuitNameStatusColumn())
        .map(MAP_HEADER, "map", SkipColumn())
        .map(TYPE_HEADER, "type", AutoColumn())
        .map(DIRECTION_HEADER, "direction", AutoColumn())
        .map(LOCATION_HEADER, "location", AutoColumn())
        .map(COUNTRY_HEADER, "country", AutoColumn())
        .map(LAST_LENGTH_USED_HEADER, "last_length_used", LastLengthUsedColumn())
        .map(TURNS_HEADER, "turns", IntColumn())
        .map(GRANDS_PRIX_HEADER, "grands_prix", LinksListColumn())
        .map(SEASONS_HEADER, "seasons", SeasonsColumn())
        .map(GRANDS_PRIX_HELD_HEADER, "grands_prix_held", IntColumn())
    )
