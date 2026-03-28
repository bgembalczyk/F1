import re
from typing import Any

from bs4 import Tag

from models.records.link import LinkRecord
from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.base.helpers.url import normalize_url
from scrapers.base.helpers.year_extraction import YEAR_RE
from scrapers.base.helpers.year_extraction import YearExtractor
from scrapers.drivers.infobox.parsers.constants import TWO_DIGIT_YEAR_SUFFIX

_YEAR_FINDALL_RE = re.compile(r"\b\d{4}(?:[--]\d{4})?\b")
_YEAR_RANGE_RE = re.compile(r"\b(\d{4})\s*[--]\s*(\d{2,4})\b")
_YEAR_RE = re.compile(r"\b(\d{4})\b")
_YEAR_OPTIONAL_RANGE_RE = re.compile(r"\d{4}(?:[--]\d{4})?")
_YEAR_OPTIONAL_RANGE_WS_RE = re.compile(r"\d{4}(?:\s*[--]\s*\d{2,4})?")
_YEAR_RANGE_STRICT_RE = re.compile(r"\d{4}\s*[--]\s*\d{2,4}")


class InfoboxLinkExtractor:
    def __init__(self, *, include_urls: bool, wikipedia_base: str) -> None:
        self._include_urls = include_urls
        self._wikipedia_base = wikipedia_base

    def extract_links(self, cell: Tag) -> list[LinkRecord]:
        if not self._include_urls:
            return []
        links = normalize_links(
            cell,
            full_url=lambda href: normalize_url(self._wikipedia_base, href),
            allow_local_anchors=False,
            drop_empty_text=True,
        )
        # Additional filter to remove any links with empty or whitespace-only text
        return [link for link in links if (link.get("text") or "").strip()]

    def first_link(self, cell: Tag) -> LinkRecord | None:
        links = self.extract_links(cell)
        return links[0] if links else None

    def extract_title_links(self, cell: Tag) -> list[LinkRecord]:
        links = self.extract_links(cell)
        if links:
            return links
        text = clean_infobox_text(cell.get_text("\n", strip=True)) or ""
        parts = [part.strip() for part in text.split("\n") if part.strip()]
        return [{"text": part, "url": None} for part in parts]

    def extract_year_links(self, cell: Tag) -> list[LinkRecord]:
        links = [link for link in self.extract_links(cell) if self.is_year_link(link)]
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        years = _YEAR_FINDALL_RE.findall(text)

        if not years:
            return links

        link_lookup = {link.get("text"): link for link in links if link.get("text")}
        results: list[LinkRecord] = []
        for year in years:
            link = link_lookup.get(year)
            if link:
                results.append(link)
            else:
                results.append({"text": year, "url": None})
        return results

    def extract_year_range_links(self, cell: Tag) -> list[dict[str, Any]]:
        """Extract year ranges with separate from/to links.

        Handles cases like:
        - Single year: 2014 -> {year: 2014, url: ...}
        - Range with both links: 2008-2010 -> {from: 2008, to: 2010, ...}
        - Range with one link: 2008-2009 -> interpolates missing link
        """
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        links = [link for link in self.extract_links(cell) if self.is_year_link(link)]

        # Build year -> url mapping
        year_to_url = YearExtractor.build_year_to_url_map(links)

        results: list[dict[str, Any]] = []

        # Track which years have been processed as part of ranges
        processed_years = set()

        # First, find ranges (year-year pattern)
        for match in _YEAR_RANGE_RE.finditer(text):
            start = int(match.group(1))
            end_text = match.group(2)
            if len(end_text) == TWO_DIGIT_YEAR_SUFFIX:
                end = (start // 100) * 100 + int(end_text)
            else:
                end = int(end_text)

            # Mark these years as processed
            processed_years.add(start)
            processed_years.add(end)

            url_from = year_to_url.get(start)
            url_to = year_to_url.get(end)

            # Try to interpolate missing URLs
            if url_from and not url_to:
                url_to = url_from.replace(str(start), str(end))
            elif url_to and not url_from:
                url_from = url_to.replace(str(end), str(start))

            results.append(
                {"from": start, "to": end, "url_from": url_from, "url_to": url_to},
            )

        # Then, find individual years not part of ranges
        for match in YEAR_RE.finditer(text):
            year = int(match.group(1))
            if year not in processed_years:
                processed_years.add(year)
                results.append({"year": year, "url": year_to_url.get(year)})

        return results

    @staticmethod
    def is_year_link(link: LinkRecord) -> bool:
        text = link.get("text") or ""
        if not _YEAR_OPTIONAL_RANGE_RE.fullmatch(text):
            return False
        url = (link.get("url") or "").lower()
        return not ("season" in url or "_season" in url)

    def extract_year_list_with_links(self, cell: Tag) -> list[dict[str, Any]]:
        """Extract years as a list of individual years with links.

        Similar to parse_active_years, but returns list in format:
        [{year: 2008, url: ...}, {year: 2009, url: ...}, ...]
        or [{text: "2018-2019", url: ...}] if range is part of a single link.

        Handles cases like:
        - Individual years: 2002, 2005, 2007
        - Ranges: 2007-2008 (expands and interpolates missing links)
        - Single link with range: <a>2018-2019</a> (keeps as-is, doesn't expand)
        - List items: preserves document order (e.g., 2022, 2009, 2007)
        """
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        links = self._extract_year_links(cell)

        range_links = self._extract_range_links(links)
        if range_links:
            return range_links

        list_item_result = self._extract_years_from_list_items(cell, links)
        if list_item_result:
            return list_item_result

        return self._extract_years_from_plain_text(text, links)

    def _extract_year_links(self, cell: Tag) -> list[LinkRecord]:
        all_links = self.extract_links(cell)
        return [
            link
            for link in all_links
            if _YEAR_OPTIONAL_RANGE_WS_RE.fullmatch(
                (link.get("text") or "").strip(),
            )
        ]

    @staticmethod
    def _extract_range_links(links: list[LinkRecord]) -> list[LinkRecord]:
        return [
            link
            for link in links
            if _YEAR_RANGE_STRICT_RE.fullmatch((link.get("text") or ""))
        ]

    def _extract_years_from_list_items(
        self,
        cell: Tag,
        links: list[LinkRecord],
    ) -> list[dict[str, Any]]:
        li_elements = cell.find_all("li", recursive=True)
        if not li_elements:
            return []

        result: list[dict[str, Any]] = []
        year_to_url = YearExtractor.build_year_to_url_map(links)
        for li in li_elements:
            li_text = clean_infobox_text(li.get_text(" ", strip=True)) or ""
            result.extend(self._extract_li_years(li_text, year_to_url))
        return result

    @staticmethod
    def _extract_li_years(
        li_text: str,
        year_to_url: dict[int, str],
    ) -> list[dict[str, Any]]:
        if _YEAR_RANGE_RE.search(li_text):
            years_in_li = YearExtractor.extract_years_from_text(li_text)
            li_year_to_url = YearExtractor.interpolate_urls(years_in_li, year_to_url)
            return [
                {"year": year, "url": li_year_to_url.get(year)}
                for year in sorted(years_in_li)
            ]

        year_match = YEAR_RE.search(li_text)
        if not year_match:
            return []
        year = int(year_match.group(1))
        return [{"year": year, "url": year_to_url.get(year)}]

    @staticmethod
    def _extract_years_from_plain_text(
        text: str,
        links: list[LinkRecord],
    ) -> list[dict[str, Any]]:
        year_to_url = YearExtractor.build_year_to_url_map(links)
        years_set = YearExtractor.extract_years_from_text(text)
        year_to_url = YearExtractor.interpolate_urls(years_set, year_to_url)
        return [
            {"year": year, "url": year_to_url.get(year)} for year in sorted(years_set)
        ]

    @staticmethod
    def find_link_by_text(text: str, links: list[LinkRecord]) -> LinkRecord | None:
        wanted = text.strip().lower()
        for link in links:
            link_text = (link.get("text") or "").strip().lower()
            if link_text == wanted:
                return link
        return None
