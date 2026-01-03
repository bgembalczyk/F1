import re
from typing import Any
from typing import Dict
from typing import List

from bs4 import Tag

from models.records.link import LinkRecord
from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.base.helpers.time import parse_date_text
from scrapers.drivers.infobox.parsers.link_extractor import InfoboxLinkExtractor


class InfoboxGeneralParser:
    def __init__(
        self,
        *,
        include_urls: bool,
        link_extractor: InfoboxLinkExtractor,
        general_keys: dict[str, str],
    ) -> None:
        self._include_urls = include_urls
        self._link_extractor = link_extractor
        self._general_keys = general_keys

    def parse(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        for row in rows:
            label = row.get("label")
            if not label:
                continue
            key = self._general_keys.get(label)
            if not key:
                continue
            cell = row.get("value_cell")
            if not isinstance(cell, Tag):
                continue

            if key in {"born", "died"}:
                data[key] = self._parse_date_place(cell)
            elif key in {"parents", "relatives"}:
                data[key] = self._parse_relations(cell)
            elif key == "children":
                data[key] = self._link_extractor.extract_links(cell)
            elif key == "cause_of_death":
                data[key] = clean_infobox_text(cell.get_text(" ", strip=True))

        return data

    def _parse_date_place(self, cell: Tag) -> Dict[str, Any]:
        text = clean_infobox_text(cell.get_text("\n", strip=True)) or ""
        parts = [p.strip() for p in text.split("\n") if p.strip()]
        date_text = parts[0] if parts else ""
        date_text = re.sub(r"\s*\([^)]*\)", "", date_text).strip()

        place_text = " ".join(parts[1:]).strip()
        if not place_text and date_text:
            match = re.match(
                r"^([0-9]{1,2}\s+[A-Za-z]+\s+\d{4}|[A-Za-z]+\s+\d{1,2},\s*\d{4}|\d{4})\s*(.*)$",
                date_text,
            )
            if match:
                date_text = match.group(1).strip()
                place_text = match.group(2).strip()

        place_parts = [p.strip() for p in place_text.split(",") if p.strip()]
        place: List[str | LinkRecord] = place_parts
        if self._include_urls and place_parts:
            links = self._link_extractor.extract_links(cell)
            place = [
                self._link_extractor.find_link_by_text(part, links) or part
                for part in place_parts
            ]
        parsed_date = parse_date_text(date_text or "")
        iso = parsed_date.iso
        if isinstance(iso, list):
            date_value = iso[0] if iso else None
        elif isinstance(iso, str):
            date_value = iso
        else:
            date_value = parsed_date.raw or date_text or None
        return {
            "date": date_value,
            "place": place or None,
        }

    def _parse_relations(self, cell: Tag) -> List[Dict[str, Any]]:
        links = self._link_extractor.extract_links(cell)
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        entries: List[Dict[str, Any]] = []
        for link in links:
            relation = None
            pattern = rf"{re.escape(link.get('text') or '')}\s*\(([^)]+)\)"
            match = re.search(pattern, text)
            if match:
                relation = match.group(1).strip()
            entries.append({"person": link, "relation": relation})
        return entries
