from scrapers.base.table.columns.registry import column_type_registry
from scrapers.base.table.columns.types.parsed_value import ParsedValueColumn


@column_type_registry.register("float")
def FloatColumn() -> ParsedValueColumn:
    return ParsedValueColumn(float)
