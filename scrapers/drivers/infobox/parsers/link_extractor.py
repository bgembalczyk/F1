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
        
        # Find all year patterns in text (both individual and ranges)
        processed_positions = set()
        
        # First, find ranges (year-year pattern)
        for match in re.finditer(r'\b(\d{4})\s*[-–]\s*(\d{2,4})\b', text):
            start = int(match.group(1))
            end_text = match.group(2)
            if len(end_text) == 2:
                end = (start // 100) * 100 + int(end_text)
            else:
                end = int(end_text)
            
            # Mark these positions as processed
            processed_positions.add(match.start())
            
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
            if match.start() not in processed_positions:
                year = int(match.group(1))
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

    @staticmethod
    def find_link_by_text(text: str, links: List[LinkRecord]) -> LinkRecord | None:
        wanted = text.strip().lower()
        for link in links:
            link_text = (link.get("text") or "").strip().lower()
            if link_text == wanted:
                return link
        return None
