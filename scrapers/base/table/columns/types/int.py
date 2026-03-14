from scrapers.base.table.columns.types.parsed_value import ParsedValueColumn


def IntColumn() -> ParsedValueColumn:  # noqa: N802
    return ParsedValueColumn(int)
