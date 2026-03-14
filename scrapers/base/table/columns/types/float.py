from scrapers.base.table.columns.types.parsed_value import ParsedValueColumn


def FloatColumn() -> ParsedValueColumn:  # noqa: N802
    return ParsedValueColumn(float)
