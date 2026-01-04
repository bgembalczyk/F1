import re
from typing import Any
from typing import Dict
from typing import List

from bs4 import Tag

from models.records.link import LinkRecord
from scrapers.base.errors import DomainParseError
from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.base.helpers.time import parse_date_text
from scrapers.base.infobox.schema import InfoboxSchema
from scrapers.drivers.infobox.parsers.link_extractor import InfoboxLinkExtractor


class InfoboxGeneralParser:
    # Date pattern for matching common date formats
    _DATE_PATTERN = r'\b\d{1,2}\s+[A-Za-z]+\s+\d{4}|\b[A-Za-z]+\s+\d{1,2},\s*\d{4}|\b\d{4}\b'
    
    def __init__(
        self,
        *,
        include_urls: bool,
        link_extractor: InfoboxLinkExtractor,
        schema: InfoboxSchema,
        logger=None,
    ) -> None:
        self._include_urls = include_urls
        self._link_extractor = link_extractor
        self._schema = schema
        self._logger = logger

    def parse(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        present_keys: set[str] = set()
        for row in rows:
            label = row.get("label")
            if not label:
                continue
            field = self._schema.field_for_label(label)
            if not field:
                continue
            key = field.key
            cell = row.get("value_cell")
            if not isinstance(cell, Tag):
                continue

            present_keys.add(key)
            if field.parser == "date_place":
                data[key] = self._parse_date_place(cell)
            elif field.parser == "relations":
                data[key] = self._parse_relations(cell)
            elif field.parser == "links":
                data[key] = self._link_extractor.extract_links(cell)
            elif field.parser == "text":
                data[key] = clean_infobox_text(cell.get_text(" ", strip=True))

        self._schema.log_missing(present_keys, logger=self._logger)
        return data

    def _parse_date_place(self, cell: Tag) -> Dict[str, Any]:
        # Try to extract date from structured data (bday class)
        bday_span = cell.find("span", class_="bday")
        if bday_span:
            date_text = clean_infobox_text(bday_span.get_text(strip=True)) or ""
        else:
            # Fallback to text-based extraction
            text = clean_infobox_text(cell.get_text("\n", strip=True)) or ""
            parts = [p.strip() for p in text.split("\n") if p.strip()]
            
            # Filter out the original name (first part if it doesn't contain date pattern)
            filtered_parts = []
            for part in parts:
                # Skip parts that look like names (no date pattern and no numbers)
                if not re.search(self._DATE_PATTERN, part):
                    # This might be the original name, skip it
                    continue
                filtered_parts.append(part)
            
            date_text = filtered_parts[0] if filtered_parts else ""
            date_text = re.sub(r"\s*\([^)]*\)", "", date_text).strip()
        
        # Extract place from birthplace span if available
        birthplace_span = cell.find("span", class_="birthplace")
        if birthplace_span:
            place_text = clean_infobox_text(birthplace_span.get_text(" ", strip=True)) or ""
        else:
            # Fallback to parsing from text
            text = clean_infobox_text(cell.get_text("\n", strip=True)) or ""
            parts = [p.strip() for p in text.split("\n") if p.strip()]
            
            # Find the part with the date and take everything after it
            place_text = ""
            for i, part in enumerate(parts):
                if re.search(self._DATE_PATTERN, part):
                    # Found date part, check if place is on same line or next lines
                    match = re.match(
                        r"^(?:[0-9]{1,2}\s+[A-Za-z]+\s+\d{4}|[A-Za-z]+\s+\d{1,2},\s*\d{4}|\d{4})(?:\s*\([^)]*\))?\s*(.*)$",
                        part,
                    )
                    if match:
                        place_text = match.group(1).strip()
                    # Also include following parts as place
                    if i + 1 < len(parts):
                        remaining = " ".join(parts[i + 1:])
                        place_text = (place_text + " " + remaining).strip()
                    break
        
        place_parts = [p.strip() for p in place_text.split(",") if p.strip()]
        place: List[str | LinkRecord] = place_parts
        if self._include_urls and place_parts:
            # Extract links, preferring from birthplace span if available
            links_source = birthplace_span if birthplace_span else cell
            links = self._link_extractor.extract_links(links_source)
            place = [
                self._link_extractor.find_link_by_text(part, links) or part
                for part in place_parts
            ]
        try:
            parsed_date = parse_date_text(date_text or "")
        except (TypeError, ValueError) as exc:
            raise DomainParseError(
                f"Nie udało się sparsować daty miejsca: {date_text!r}.",
                cause=exc,
            ) from exc
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
