from typing import Any
from typing import Dict
from typing import List

from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.drivers.infobox.parsers.cell import InfoboxCellParser


class InfoboxCareerParser:
    def __init__(self, cell_parser: InfoboxCellParser) -> None:
        self._cell_parser = cell_parser

    def parse_section(self, title: str, section: Dict[str, Any]) -> Dict[str, Any]:
        rows: List[Dict[str, Any]] = []
        for row in section.get("rows", []):
            if "label_cell" in row and "value_cell" in row:
                label_cell = row["label_cell"]
                value_cell = row["value_cell"]
                label = clean_infobox_text(label_cell.get_text(" ", strip=True))
                if label in {"Active years", "Years active"}:
                    value = self._cell_parser.parse_active_years(value_cell)
                elif label == "Years":
                    value = self._cell_parser.parse_active_years(value_cell)
                elif label == "Car number":
                    value = self._cell_parser.parse_car_numbers(value_cell)
                elif label == "Teams":
                    value = self._cell_parser.parse_teams(value_cell)
                elif label == "Entries":
                    value = self._cell_parser.parse_entries(value_cell)
                elif label == "Championships":
                    value = self._cell_parser.parse_championships(value_cell)
                elif label == "Class wins":
                    value = self._cell_parser.parse_class_wins(value_cell)
                elif label in {
                    "Wins",
                    "Podiums",
                    "Pole positions",
                    "Poles",
                    "Fastest laps",
                    "Starts",
                }:
                    value = self._cell_parser.parse_int_cell(value_cell)
                elif label == "Career points":
                    value = self._cell_parser.parse_float_cell(value_cell)
                elif label == "Best finish":
                    value = self._cell_parser.parse_best_finish(value_cell)
                elif label in {"First race", "Last race", "First win", "Last win", "First entry", "Last entry"}:
                    value = self._cell_parser.parse_race_event(value_cell)
                elif label == "Former teams":
                    value = self._cell_parser.parse_teams(value_cell)
                elif label == "Finished last season":
                    value = self._cell_parser.parse_finished_last_season(value_cell)
                elif label == "Racing licence":
                    value = self._cell_parser.parse_racing_licence(value_cell)
                else:
                    value = self._cell_parser.parse_cell(value_cell)
                rows.append(
                    {
                        "label": label,
                        "value": value,
                    }
                )
            elif "full_data_cell" in row:
                rows.append(
                    {"full_data": self._cell_parser.parse_full_data(row["full_data_cell"])}
                )
        return {"title": title, "rows": rows}
