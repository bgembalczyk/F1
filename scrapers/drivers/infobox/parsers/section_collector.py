from typing import Any

from bs4 import Tag

from scrapers.base.helpers.text_normalization import clean_infobox_text


class InfoboxSectionCollector:
    @staticmethod
    def collect(table: Tag) -> list[dict[str, Any]]:
        sections: list[dict[str, Any]] = [{"title": None, "rows": []}]
        current = sections[0]

        for tr in table.find_all("tr"):
            if tr.find_parent("table") is not table:
                continue

            header = tr.find("th", class_="infobox-header")
            if header:
                title = clean_infobox_text(header.get_text(" ", strip=True))
                if title:
                    current = {"title": title, "rows": []}
                    sections.append(current)
                continue

            label = tr.find("th", class_="infobox-label")
            value = tr.find("td", class_="infobox-data")
            if label and value:
                current["rows"].append(
                    {
                        "label": clean_infobox_text(label.get_text(" ", strip=True)),
                        "label_cell": label,
                        "value_cell": value,
                    },
                )
                continue

            full_data = tr.find(["td", "th"], class_="infobox-full-data")
            if full_data:
                # Check if this contains a collapsible table with career statistics
                nested_table = full_data.find("table", class_="mw-collapsible")
                if nested_table:
                    # Parse collapsible career statistics table
                    current["rows"].append(
                        {
                            "full_data_cell": full_data,
                            "collapsible_table": nested_table,
                        },
                    )
                else:
                    current["rows"].append({"full_data_cell": full_data})

        return sections
