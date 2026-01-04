import re
from typing import Any
from typing import Dict
from typing import List

from bs4 import BeautifulSoup, Tag

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
            
            # Split by <br> tags to match series with year groups
            series_groups = self._split_by_br(value_cell)
            year_groups = self._split_by_br(label_cell)
            
            # If we have the same number of groups, pair them up
            if len(series_groups) == len(year_groups) and len(series_groups) > 1:
                for series_html, year_html in zip(series_groups, year_groups):
                    series_soup = BeautifulSoup(series_html, 'html.parser')
                    year_soup = BeautifulSoup(year_html, 'html.parser')
                    series_links = self._link_extractor.extract_title_links(series_soup)
                    year_data = self._link_extractor.extract_year_list_with_links(year_soup)
                    
                    if series_links:
                        items.append({"title": series_links[0], "years": year_data})
                    else:
                        series_text = clean_infobox_text(series_soup.get_text(" ", strip=True))
                        items.append(
                            {"title": {"text": series_text or "", "url": None}, "years": year_data}
                        )
            else:
                # Fall back to original logic for single group or mismatched counts
                series_links = self._link_extractor.extract_title_links(value_cell)
                year_data = self._link_extractor.extract_year_list_with_links(label_cell)
                
                if series_links and year_data:
                    items.append({"title": series_links[0], "years": year_data})
                elif series_links:
                    for series_link in series_links:
                        items.append({"title": series_link, "years": []})
                else:
                    series_text = clean_infobox_text(value_cell.get_text(" ", strip=True))
                    items.append(
                        {"title": {"text": series_text or "", "url": None}, "years": year_data}
                    )
        return items
    
    @staticmethod
    def _split_by_br(tag: Tag) -> List[str]:
        """Split HTML content by <br> tags."""
        from bs4 import BeautifulSoup
        html = str(tag)
        # Split by <br> and variants
        parts = re.split(r'<br\s*/?>', html, flags=re.IGNORECASE)
        # Filter out empty parts
        return [p.strip() for p in parts if p.strip()]
