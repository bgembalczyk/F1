import re
from typing import List

from bs4 import Tag

from models.records.link import LinkRecord
from scrapers.base.helpers.text import extract_links_from_cell
from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.base.helpers.wiki import build_full_url


class InfoboxLinkExtractor:
    def __init__(self, *, include_urls: bool, wikipedia_base: str) -> None:
        self._include_urls = include_urls
        self._wikipedia_base = wikipedia_base

    def extract_links(self, cell: Tag) -> List[LinkRecord]:
        if not self._include_urls:
            return []
        return extract_links_from_cell(
            cell,
            full_url=lambda href: build_full_url(self._wikipedia_base, href),
            allow_local_anchors=False,
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
