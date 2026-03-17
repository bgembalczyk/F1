from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.grands_prix.columns.race_title_status import RaceTitleStatusColumn


def build_grands_prix_list_schema() -> TableSchemaDSL:
    return TableSchemaDSL(
        columns=[
            column("Race title", "race_title", RaceTitleStatusColumn()),
            column("Country", "country", LinksListColumn()),
            column("Years held", "years_held", SeasonsColumn()),
            column("Circuits", "circuits", IntColumn()),
            column("Total", "total", IntColumn()),
        ],
    )
