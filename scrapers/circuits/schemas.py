from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.circuits.sections.list_table import CircuitsListTableParser


def build_circuits_schema() -> TableSchemaDSL:
    return CircuitsListTableParser.build_schema()
