import re
from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.drivers.infobox.parsers.link_extractor import InfoboxLinkExtractor


class InfoboxTitlesParser:
    def __init__(self, link_extractor: InfoboxLinkExtractor) -> None:
        self._link_extractor = link_extractor

    def parse_titles(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        titles: list[dict[str, Any]] = []
        for row in rows:
            label_cell = row.get("label_cell")
            value_cell = row.get("value_cell")
            if not isinstance(label_cell, Tag) or not isinstance(value_cell, Tag):
                continue

            title_links = self._link_extractor.extract_title_links(value_cell)
            # Use extract_year_list_with_links to expand year ranges to individual years
            year_data = self._link_extractor.extract_year_list_with_links(label_cell)

            if (
                title_links
                and year_data
                and len(title_links) == len(year_data)
                and len(title_links) > 1
            ):
                for title_link, year_item in zip(title_links, year_data, strict=False):
                    titles.append({"title": title_link, "years": [year_item]})
                continue

            if title_links and year_data:
                titles.append({"title": title_links[0], "years": year_data})
                continue

            if title_links:
                for title_link in title_links:
                    titles.append({"title": title_link, "years": []})
                continue

            title_text = clean_infobox_text(value_cell.get_text(" ", strip=True))
            titles.append(
                {"title": {"text": title_text or "", "url": None}, "years": year_data},
            )

        return titles

    def parse_previous_series(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for row in rows:
            label_cell = row.get("label_cell")
            value_cell = row.get("value_cell")
            if not isinstance(label_cell, Tag) or not isinstance(value_cell, Tag):
                continue

            # Try splitting by <li> tags first (list items)
            series_groups = self._split_by_list_items(value_cell)
            year_groups = self._split_by_list_items(label_cell)

            # If no list items found, try splitting by <br> tags
            if len(series_groups) <= 1:
                series_groups = self._split_by_br(value_cell)
            if len(year_groups) <= 1:
                year_groups = self._split_by_br(label_cell)

            # If we have the same number of groups, pair them up
            if len(series_groups) == len(year_groups) and len(series_groups) > 1:
                for series_html, year_html in zip(
                    series_groups,
                    year_groups,
                    strict=False,
                ):
                    series_soup = BeautifulSoup(series_html, "html.parser")
                    year_soup = BeautifulSoup(year_html, "html.parser")
                    series_links = self._link_extractor.extract_title_links(series_soup)
                    year_data = self._link_extractor.extract_year_list_with_links(
                        year_soup,
                    )

                    if series_links:
                        items.append({"title": series_links[0], "years": year_data})
                    else:
                        series_text = clean_infobox_text(
                            series_soup.get_text(" ", strip=True),
                        )
                        items.append(
                            {
                                "title": {"text": series_text or "", "url": None},
                                "years": year_data,
                            },
                        )
            else:
                # Fall back to original logic for single group or mismatched counts
                series_links = self._link_extractor.extract_title_links(value_cell)
                year_data = self._link_extractor.extract_year_list_with_links(
                    label_cell,
                )

                if series_links and year_data:
                    items.append({"title": series_links[0], "years": year_data})
                elif series_links:
                    for series_link in series_links:
                        items.append({"title": series_link, "years": []})
                else:
                    series_text = clean_infobox_text(
                        value_cell.get_text(" ", strip=True),
                    )
                    items.append(
                        {
                            "title": {"text": series_text or "", "url": None},
                            "years": year_data,
                        },
                    )
        return items

    @staticmethod
    def _split_by_list_items(tag: Tag) -> list[str]:
        """Split HTML content by <li> list items."""
        # Find all <li> elements
        li_elements = tag.find_all("li", recursive=True)
        if not li_elements:
            return []
        # Return the HTML content of each <li>
        return [str(li) for li in li_elements if str(li).strip()]

    @staticmethod
    def _split_by_br(tag: Tag) -> list[str]:
        """Split HTML content by <br> tags."""

        html = str(tag)
        # Split by <br> and variants
        parts = re.split(r"<br\s*/?>", html, flags=re.IGNORECASE)
        # Filter out empty parts
        return [p.strip() for p in parts if p.strip()]

    def parse_major_victories_from_full_data(self, cell: Tag) -> list[dict[str, Any]]:
        """Parse major victories from a full_data cell.

        Handles HTML like:
        <b>Major victories</b> <br>
        <a href="/wiki/24_Hours_of_Le_Mans" title="24 Hours of Le Mans">24 Hours of Le Mans</a>
        (<a href="/wiki/1934_24_Hours_of_Le_Mans" title="1934 24 Hours of Le Mans">1934</a>)
        """
        victories: list[dict[str, Any]] = []

        # Get text and check if it contains "Major victories"
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        if "major victories" not in text.lower():
            return victories

        # Extract all links from the cell
        all_links = self._link_extractor.extract_links(cell)

        # Filter out links that are years (4 digits)
        event_links = []
        year_links = []

        for link in all_links:
            link_text = link.get("text", "")
            # Check if link text is a year
            if re.fullmatch(r"\d{4}", link_text):
                year_links.append(link)
            else:
                event_links.append(link)

        # Group event links with their associated year links
        # Strategy: for each event link, find year links that come after it in the text
        for event_link in event_links:
            event_text = event_link.get("text", "")

            # Find this event in the text
            event_index = text.find(event_text)
            if event_index < 0:
                continue

            # Find year links that appear after this event
            associated_years = []
            for year_link in year_links:
                year_text = year_link.get("text", "")
                year_index = text.find(year_text, event_index)
                if year_index >= event_index:
                    # Check if this year is before the next event
                    # Find next event link position
                    next_event_index = len(text)
                    for other_event in event_links:
                        if other_event == event_link:
                            continue
                        other_event_text = other_event.get("text", "")
                        other_index = text.find(other_event_text, event_index + 1)
                        if event_index < other_index < next_event_index:
                            next_event_index = other_index

                    if year_index < next_event_index:
                        associated_years.append(year_link)

            victories.append({"title": event_link, "years": associated_years})

        return victories
