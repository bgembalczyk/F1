from scrapers.base.table.columns.types.parsed_value import ParsedValueColumn


def FloatColumn() -> ParsedValueColumn:
    return ParsedValueColumn(float)
