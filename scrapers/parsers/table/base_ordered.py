from scrapers.parsers.table.wiki.base import WikiTableBaseParser


class DriverOrderedTableParser(WikiTableBaseParser):
    """Base parser for driver tables that orders the 'driver' column first."""

    _column_mapping: dict[str, str]

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        mapped_headers = [
            header
            for header in headers
            if header in getattr(self, "_column_mapping", {})
        ]
        driver_headers = [
            header
            for header in mapped_headers
            if self._column_mapping[header] == "driver"
        ]
        other_headers = [
            header
            for header in mapped_headers
            if self._column_mapping[header] != "driver"
        ]
        return {
            header: self._column_mapping[header]
            for header in [*driver_headers, *other_headers]
        }


__all__ = ["DriverOrderedTableParser"]
