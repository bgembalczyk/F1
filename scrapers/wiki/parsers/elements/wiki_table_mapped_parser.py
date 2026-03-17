from scrapers.wiki.parsers.elements.wiki_table_base_parser import WikiTableBaseParser


class MappedWikiTableParser(WikiTableBaseParser):
    required_header_groups: tuple[frozenset[str], ...] = ()
    column_mapping: dict[str, str] = {}

    def matches(self, headers: list[str], _table_data: dict[str, object]) -> bool:
        header_set = set(headers)
        return all(bool(header_set & group) for group in self.required_header_groups)

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {
            header: self.column_mapping[header]
            for header in headers
            if header in self.column_mapping
        }
