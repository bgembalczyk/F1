from scrapers.base.table.columns.types.parsed_value import ParsedValueColumn


def IntColumn() -> ParsedValueColumn:
    return ParsedValueColumn(int)
