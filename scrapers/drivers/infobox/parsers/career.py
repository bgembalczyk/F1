from typing import Any

from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.drivers.infobox.parsers.career_label_parsers import parser_for_label
from scrapers.drivers.infobox.parsers.cell import InfoboxCellParser


class InfoboxCareerParser:
    def __init__(self, cell_parser: InfoboxCellParser) -> None:
        self._cell_parser = cell_parser

    def parse_section(self, title: str, section: dict[str, Any]) -> dict[str, Any]:
        rows: list[dict[str, Any]] = []
        for row in section.get("rows", []):
            parsed = self._parse_row(row)
            if parsed is not None:
                rows.append(parsed)
        return {"title": title, "rows": rows}

    def _parse_row(self, row: dict[str, Any]) -> dict[str, Any] | None:
        if "label_cell" in row and "value_cell" in row:
            return self._parse_label_value_row(row)
        if "full_data_cell" in row:
            return self._parse_full_data_row(row)
        return None

    def _parse_label_value_row(self, row: dict[str, Any]) -> dict[str, Any]:
        label_cell = row["label_cell"]
        value_cell = row["value_cell"]
        label = clean_infobox_text(label_cell.get_text(" ", strip=True))
        value = self._parse_value_for_label(label, value_cell)
        return {"label": label, "value": value}

    def _parse_value_for_label(self, label: str | None, value_cell: Any) -> Any:
        parser = parser_for_label(label=label, cell_parser=self._cell_parser)
        return parser(value_cell)


    def _parse_full_data_row(self, row: dict[str, Any]) -> dict[str, Any] | None:
        if "collapsible_table" in row:
            career_stats = self._cell_parser.parse_collapsible_career_table(
                row["collapsible_table"],
            )
            return {"collapsible_career": career_stats} if career_stats else None
        return {"full_data": self._cell_parser.parse_full_data(row["full_data_cell"])}
