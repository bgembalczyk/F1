from scrapers.wiki.parsers.elements.wiki_table.base import WikiTableBaseParser


class CircuitsListTableParser(WikiTableBaseParser):
    """Specialized wikitable parser for the circuits list table."""

    table_type = "circuits_list"
    missing_columns_policy = "require_core_circuit_columns"
    extra_columns_policy = "ignore"

    _required_headers = frozenset({"Circuit", "Type", "Location", "Country"})
    _column_mapping = {
        "Circuit": "circuit",
        "Type": "type",
        "Location": "location",
        "Country": "country",
    }

    def matches(self, headers: list[str], _table_data: dict[str, object]) -> bool:
        return self._required_headers.issubset(set(headers))

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {
            header: self._column_mapping[header]
            for header in headers
            if header in self._column_mapping
        }
