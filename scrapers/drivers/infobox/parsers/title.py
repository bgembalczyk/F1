from typing import Any
from typing import Dict
from typing import List

from bs4 import Tag

from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.drivers.infobox.parsers.link_extractor import InfoboxLinkExtractor


class InfoboxTitlesParser:
    def __init__(self, link_extractor: InfoboxLinkExtractor) -> None:
        self._link_extractor = link_extractor

    def parse_titles(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        titles: List[Dict[str, Any]] = []
        for row in rows:
            label_cell = row.get("label_cell")
            value_cell = row.get("value_cell")
            if not isinstance(label_cell, Tag) or not isinstance(value_cell, Tag):
                continue

            title_links = self._link_extractor.extract_title_links(value_cell)
            year_links = self._link_extractor.extract_year_links(label_cell)

            if (
                title_links
                and year_links
                and len(title_links) == len(year_links)
                and len(title_links) > 1
            ):
                for title_link, year_link in zip(title_links, year_links):
                    titles.append({"title": title_link, "years": [year_link]})
                continue

            if title_links and year_links:
                titles.append({"title": title_links[0], "years": year_links})
                continue

            if title_links:
                for title_link in title_links:
                    titles.append({"title": title_link, "years": []})
                continue

            title_text = clean_infobox_text(value_cell.get_text(" ", strip=True))
            titles.append(
                {"title": {"text": title_text or "", "url": None}, "years": year_links}
            )

        return titles

    def parse_previous_series(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        for row in rows:
            label_cell = row.get("label_cell")
            value_cell = row.get("value_cell")
            if not isinstance(label_cell, Tag) or not isinstance(value_cell, Tag):
                continue
            series_links = self._link_extractor.extract_title_links(value_cell)
            year_data = self._link_extractor.extract_year_range_links(label_cell)
            
            if (
                series_links
                and year_data
                and len(series_links) == len(year_data)
                and len(series_links) > 1
            ):
                for series_link, year_info in zip(series_links, year_data):
                    items.append({"title": series_link, "years": [year_info]})
                continue
            if series_links and year_data:
                items.append({"title": series_links[0], "years": year_data})
                continue
            if series_links:
                for series_link in series_links:
                    items.append({"title": series_link, "years": []})
                continue
            series_text = clean_infobox_text(value_cell.get_text(" ", strip=True))
            items.append(
                {"title": {"text": series_text or "", "url": None}, "years": year_data}
            )
        return items
