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
    _DATE_PATTERN = (
        r"\b\d{1,2}\s+[A-Za-z]+\s+\d{4}|\b[A-Za-z]+\s+\d{1,2},\s*\d{4}|\b\d{4}\b"
    )

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
        date_text = self._extract_date_text(cell)
        place = self._extract_place(cell)
        date_value = self._normalize_date_value(date_text)
        return {
            "date": date_value,
            "place": place or None,
        }

    def _extract_date_text(self, cell: Tag) -> str:
        """Extract date text from cell using structured data or fallback."""
        # Try to extract date from structured data (bday or dday class)
        bday_span = cell.find("span", class_="bday")
        dday_span = cell.find("span", class_="dday")

        if bday_span:
            return clean_infobox_text(bday_span.get_text(strip=True)) or ""
        elif dday_span:
            return clean_infobox_text(dday_span.get_text(strip=True)) or ""

        # Try to find hidden span with ISO date format (style="display:none")
        iso_date = self._extract_iso_date_from_hidden_span(cell)
        if iso_date:
            return iso_date

        # Fallback to text-based extraction
        return self._extract_date_from_text(cell)

    def _extract_iso_date_from_hidden_span(self, cell: Tag) -> str | None:
        """Extract ISO date from hidden span elements."""
        hidden_spans = cell.find_all(
            "span", style=lambda x: x and "display:none" in x,
        )
        for span in hidden_spans:
            span_text = span.get_text(strip=True)
            # Look for ISO date pattern in parentheses
            iso_match = re.search(r"\((\d{4}-\d{2}-\d{2})\)", span_text)
            if iso_match:
                return iso_match.group(1)
        return None

    def _extract_date_from_text(self, cell: Tag) -> str:
        """Extract date from cell text when structured data is not available."""
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
        return re.sub(r"\s*\([^)]*\)", "", date_text).strip()

    def _extract_place(self, cell: Tag) -> List[str | LinkRecord]:
        """Extract place information from cell."""
        # Extract place from birthplace/deathplace element (div or span) if available
        place_span = cell.find(class_="birthplace") or cell.find(class_="deathplace")
        if place_span:
            return self._extract_place_from_span(place_span)
        else:
            return self._extract_place_from_text(cell)

    def _extract_place_from_span(self, place_span: Tag) -> List[str | LinkRecord]:
        """Extract place from birthplace/deathplace span element."""
        place_text = clean_infobox_text(place_span.get_text(" ", strip=True)) or ""

        if self._include_urls:
            links = self._link_extractor.extract_links(place_span)
            if links:
                # Build place from links and remaining text
                place: List[str | LinkRecord] = []
                remaining_text = place_text

                # Remove link texts from remaining_text to find non-linked parts
                for link in links:
                    link_text = link.get("text", "")
                    if link_text in remaining_text:
                        remaining_text = remaining_text.replace(link_text, "", 1)

                # Clean up remaining text (remove extra commas and spaces)
                remaining_text = re.sub(r"\s*,\s*", ", ", remaining_text).strip(", ")

                # Combine links and remaining text parts
                place.extend(links)
                if remaining_text:
                    remaining_parts = [
                        p.strip() for p in remaining_text.split(",") if p.strip()
                    ]
                    place.extend(remaining_parts)
                return place
            else:
                # No links, just split by comma
                return [p.strip() for p in place_text.split(",") if p.strip()]
        else:
            # No URL extraction, just split by comma
            return [p.strip() for p in place_text.split(",") if p.strip()]

    def _extract_place_from_text(self, cell: Tag) -> List[str | LinkRecord]:
        """Fallback method to extract place from cell text."""
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

        # Filter out "(aged X)" pattern from place text
        place_text = re.sub(r"\s*\(aged\s+\d+\)", "", place_text, flags=re.IGNORECASE)

        place_parts = [p.strip() for p in place_text.split(",") if p.strip()]
        place: List[str | LinkRecord] = place_parts

        if self._include_urls and place_parts:
            # Extract links from cell (not from span since we don't have one)
            links = self._link_extractor.extract_links(cell)
            place = [
                self._link_extractor.find_link_by_text(part, links) or part
                for part in place_parts
            ]

        return place

    def _normalize_date_value(self, date_text: str) -> str | None:
        """Normalize date text to standard format."""
        try:
            parsed_date = parse_date_text(date_text or "")
        except (TypeError, ValueError) as exc:
            raise DomainParseError(
                f"Nie udało się sparsować daty miejsca: {date_text!r}.",
                cause=exc,
            ) from exc

        iso = parsed_date.iso
        if isinstance(iso, list):
            return iso[0] if iso else None
        elif isinstance(iso, str):
            return iso
        else:
            return parsed_date.raw or date_text or None

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
