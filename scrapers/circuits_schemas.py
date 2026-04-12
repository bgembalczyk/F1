from scrapers.mappers.circuit_list_table_mapper import TABLE_SCHEMA
from scrapers.table_schema_dsl import TableSchemaDSL


def build_circuits_schema() -> TableSchemaDSL:
    return TABLE_SCHEMA
