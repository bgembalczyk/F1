import re
from typing import Any, Dict, List

from bs4 import Tag

from models.records.link import LinkRecord
from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.base.helpers.url import normalize_url


class InfoboxLinkExtractor:
    def __init__(self, *, include_urls: bool, wikipedia_base: str) -> None:
        self._include_urls = include_urls
        self._wikipedia_base = wikipedia_base

    def extract_links(self, cell: Tag) -> List[LinkRecord]:
        if not self._include_urls:
            return []
        return normalize_links(
            cell,
            full_url=lambda href: normalize_url(self._wikipedia_base, href),
            allow_local_anchors=False,
            drop_empty_text=True,
        )

    def first_link(self, cell: Tag) -> LinkRecord | None:
        links = self.extract_links(cell)
        return links[0] if links else None

    def extract_title_links(self, cell: Tag) -> List[LinkRecord]:
        links = self.extract_links(cell)
        if links:
            return links
        text = clean_infobox_text(cell.get_text("\n", strip=True)) or ""
        parts = [part.strip() for part in text.split("\n") if part.strip()]
        return [{"text": part, "url": None} for part in parts]

    def extract_year_links(self, cell: Tag) -> List[LinkRecord]:
        links = [link for link in self.extract_links(cell) if self.is_year_link(link)]
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        years = re.findall(r"\b\d{4}(?:[-–]\d{4})?\b", text)

        if not years:
            return links

        link_lookup = {link.get("text"): link for link in links if link.get("text")}
        results: List[LinkRecord] = []
        for year in years:
            link = link_lookup.get(year)
            if link:
                results.append(link)
            else:
                results.append({"text": year, "url": None})
        return results
    
    def extract_year_range_links(self, cell: Tag) -> List[Dict[str, Any]]:
        """Extract year ranges with separate from/to links.
        
        Handles cases like:
        - Single year: 2014 -> {year: 2014, url: ...}
        - Range with both links: 2008–2010 -> {from: 2008, to: 2010, url_from: ..., url_to: ...}
        - Range with one link: 2008–2009 -> interpolates missing link if pattern is detected
        """
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        links = [link for link in self.extract_links(cell) if self.is_year_link(link)]
        
        # Build year -> url mapping
        year_to_url: Dict[int, str | None] = {}
        for link in links:
            link_text = link.get("text", "")
            year_match = re.search(r'\b(\d{4})\b', link_text)
            if year_match:
                year = int(year_match.group(1))
                year_to_url[year] = link.get("url")
        
        results: List[Dict[str, Any]] = []
        
        # Track which years have been processed as part of ranges
        processed_years = set()
        
        # First, find ranges (year-year pattern)
        for match in re.finditer(r'\b(\d{4})\s*[-–]\s*(\d{2,4})\b', text):
            start = int(match.group(1))
            end_text = match.group(2)
            if len(end_text) == 2:
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
            
            results.append({
                "from": start,
                "to": end,
                "url_from": url_from,
                "url_to": url_to
            })
        
        # Then, find individual years not part of ranges
        for match in re.finditer(r'\b(\d{4})\b', text):
            year = int(match.group(1))
            if year not in processed_years:
                processed_years.add(year)
                results.append({
                    "year": year,
                    "url": year_to_url.get(year)
                })
        
        return results

    @staticmethod
    def is_year_link(link: LinkRecord) -> bool:
        text = link.get("text") or ""
        if not re.fullmatch(r"\d{4}(?:[-–]\d{4})?", text):
            return False
        url = (link.get("url") or "").lower()
        if "season" in url or "_season" in url:
            return False
        return True
    
    def extract_year_list_with_links(self, cell: Tag) -> List[Dict[str, Any]]:
        """Extract years as a list of individual years with links.
        
        Similar to parse_active_years, but returns list in format:
        [{year: 2008, url: ...}, {year: 2009, url: ...}, ...]
        
        Handles cases like:
        - Individual years: 2002, 2005, 2007
        - Ranges: 2007-2008 (expands and interpolates missing links)
        """
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        links = [link for link in self.extract_links(cell) if self.is_year_link(link)]
        
        # Build a map of year -> link
        year_to_url: Dict[int, str | None] = {}
        for link in links:
            link_text = link.get("text", "")
            year_match = re.search(r'\b(\d{4})\b', link_text)
            if year_match:
                year = int(year_match.group(1))
                year_to_url[year] = link.get("url")
        
        # Extract all years and ranges from text
        years_set: set[int] = set()
        
        # Find ranges like "2007-2008" or "2007–2008"
        for match in re.finditer(r'\b(\d{4})\s*[-–]\s*(\d{2,4})\b', text):
            start = int(match.group(1))
            end_text = match.group(2)
            if len(end_text) == 2:
                end = (start // 100) * 100 + int(end_text)
            else:
                end = int(end_text)
            for year in range(start, end + 1):
                years_set.add(year)
        
        # Find individual years
        for match in re.finditer(r'\b(\d{4})\b', text):
            year = int(match.group(1))
            years_set.add(year)
        
        # Try to interpolate URLs for missing years
        if len(year_to_url) >= 2:
            # Detect URL pattern
            url_pattern = self._detect_url_pattern(year_to_url)
            if url_pattern:
                for year in years_set:
                    if year not in year_to_url:
                        year_to_url[year] = url_pattern.replace("{year}", str(year))
        
        # Build result list
        result = []
        for year in sorted(years_set):
            result.append({
                "year": year,
                "url": year_to_url.get(year)
            })
        
        return result
    
    @staticmethod
    def _detect_url_pattern(year_to_url: Dict[int, str | None]) -> str | None:
        """Detect a predictable URL pattern from available year links.
        
        Returns a pattern string with {year} placeholder if pattern is predictable.
        """
        urls = [(year, url) for year, url in year_to_url.items() if url]
        if len(urls) < 2:
            return None
        
        # Check if all URLs follow the same pattern
        patterns = []
        for year, url in urls:
            # Replace the year in URL with a placeholder
            pattern = url.replace(str(year), "{year}")
            patterns.append(pattern)
        
        # If all patterns are the same, we found a predictable pattern
        if len(set(patterns)) == 1:
            return patterns[0]
        
        return None

    @staticmethod
    def find_link_by_text(text: str, links: List[LinkRecord]) -> LinkRecord | None:
        wanted = text.strip().lower()
        for link in links:
            link_text = (link.get("text") or "").strip().lower()
            if link_text == wanted:
                return link
        return None
