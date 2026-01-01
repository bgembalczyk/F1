from __future__ import annotations

import re
from typing import Any, Dict, List

from bs4 import BeautifulSoup, Tag

from models.records.link import LinkRecord
from scrapers.base.helpers.html_utils import extract_links_from_cell
from scrapers.base.helpers.text_normalization import clean_infobox_text, clean_wiki_text
from scrapers.base.helpers.time import parse_date_text
from scrapers.base.helpers.wiki import build_full_url
from scrapers.base.infobox.html_parser import InfoboxHtmlParser
from scrapers.base.options import ScraperOptions


class DriverInfoboxScraper:
    _IGNORED_SECTIONS = {"Awards", "Medal record", "Signature"}
    _GENERAL_KEYS = {
        "Born": "born",
        "Died": "died",
        "Parent": "parents",
        "Parents": "parents",
        "Parent(s)": "parents",
        "Relatives": "relatives",
        "Children": "children",
        "Cause of death": "cause_of_death",
    }

    def __init__(self, *, options: ScraperOptions | None = None) -> None:
        options = options or ScraperOptions()
        self.include_urls = options.include_urls
        self.wikipedia_base = InfoboxHtmlParser.WIKIPEDIA_BASE

    def parse(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        table = InfoboxHtmlParser.find_infobox(soup)
        if table is None:
            return []
        return [self._parse_infobox(table)]

    def _parse_infobox(self, table: Tag) -> Dict[str, Any]:
        sections = self._collect_sections(table)
        general_section = sections[0] if sections else {"rows": []}

        parsed = {
            "title": self._infobox_title(table),
            "general": self._parse_general(general_section.get("rows", [])),
            "championship_titles": [],
            "major_victories": [],
            "career": [],
            "previous_series": [],
        }

        for section in sections[1:]:
            title = section.get("title") or ""
            if title in self._IGNORED_SECTIONS:
                continue
            if title == "Championship titles":
                parsed["championship_titles"] = self._parse_titles(section["rows"])
                continue
            if title == "Major victories":
                parsed["major_victories"] = self._parse_titles(section["rows"])
                continue
            if title.endswith("career"):
                parsed["career"].append(self._parse_career_section(title, section))
                continue
            if title == "Previous series":
                parsed["previous_series"] = self._parse_previous_series(section["rows"])
                continue

        return parsed

    def _infobox_title(self, table: Tag) -> str | None:
        caption = table.find("caption")
        if not caption:
            return None
        return clean_infobox_text(caption.get_text(" ", strip=True))

    def _collect_sections(self, table: Tag) -> List[Dict[str, Any]]:
        sections: List[Dict[str, Any]] = [{"title": None, "rows": []}]
        current = sections[0]

        for tr in table.find_all("tr"):
            if tr.find_parent("table") is not table:
                continue

            header = tr.find("th", class_="infobox-header")
            if header:
                title = clean_infobox_text(header.get_text(" ", strip=True))
                if title:
                    current = {"title": title, "rows": []}
                    sections.append(current)
                continue

            label = tr.find("th", class_="infobox-label")
            value = tr.find("td", class_="infobox-data")
            if label and value:
                current["rows"].append(
                    {
                        "label": clean_infobox_text(label.get_text(" ", strip=True)),
                        "label_cell": label,
                        "value_cell": value,
                    }
                )
                continue

            full_data = tr.find(["td", "th"], class_="infobox-full-data")
            if full_data:
                current["rows"].append({"full_data_cell": full_data})

        return sections

    def _parse_general(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        for row in rows:
            label = row.get("label")
            if not label:
                continue
            key = self._GENERAL_KEYS.get(label)
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
                data[key] = self._extract_links(cell)
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
        if self.include_urls and place_parts:
            links = self._extract_links(cell)
            place = [
                self._find_link_by_text(part, links) or part for part in place_parts
            ]
        parsed_date = parse_date_text(date_text or "")
        iso = parsed_date.get("iso")
        if isinstance(iso, list):
            date_value = iso[0] if iso else None
        elif isinstance(iso, str):
            date_value = iso
        else:
            date_value = date_text or None
        return {
            "date": date_value,
            "place": place or None,
        }

    def _parse_relations(self, cell: Tag) -> List[Dict[str, Any]]:
        links = self._extract_links(cell)
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

    def _parse_titles(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        titles: List[Dict[str, Any]] = []
        for row in rows:
            label_cell = row.get("label_cell")
            value_cell = row.get("value_cell")
            if not isinstance(label_cell, Tag) or not isinstance(value_cell, Tag):
                continue

            title_link = self._first_link(label_cell)
            if title_link is None:
                title_text = clean_infobox_text(label_cell.get_text(" ", strip=True))
                title_link = {"text": title_text or "", "url": None}

            years = self._extract_year_links(label_cell) + self._extract_year_links(
                value_cell
            )
            titles.append({"title": title_link, "years": years})

        return titles

    def _parse_career_section(self, title: str, section: Dict[str, Any]) -> Dict[str, Any]:
        rows: List[Dict[str, Any]] = []
        for row in section.get("rows", []):
            if "label_cell" in row and "value_cell" in row:
                label_cell = row["label_cell"]
                value_cell = row["value_cell"]
                rows.append(
                    {
                        "label": clean_infobox_text(
                            label_cell.get_text(" ", strip=True)
                        ),
                        "value": self._parse_cell(value_cell),
                    }
                )
            elif "full_data_cell" in row:
                rows.append({"full_data": self._parse_full_data(row["full_data_cell"])})
        return {"title": title, "rows": rows}

    def _parse_previous_series(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        for row in rows:
            label_cell = row.get("label_cell")
            value_cell = row.get("value_cell")
            if not isinstance(label_cell, Tag) or not isinstance(value_cell, Tag):
                continue
            items.append(
                {
                    "years": self._extract_links(label_cell),
                    "series": self._extract_links(value_cell),
                }
            )
        return items

    def _parse_cell(self, cell: Tag) -> Dict[str, Any]:
        text = clean_infobox_text(cell.get_text(" ", strip=True))
        payload = {"text": text}
        if self.include_urls:
            payload["links"] = self._extract_links(cell)
        return payload

    def _parse_full_data(self, cell: Tag) -> Dict[str, Any]:
        text = clean_infobox_text(cell.get_text(" ", strip=True))
        payload: Dict[str, Any] = {"text": text}
        if self.include_urls:
            payload["links"] = self._extract_links(cell)

        nested_table = cell.find("table")
        if nested_table:
            payload["table"] = self._parse_nested_table(nested_table)
        return payload

    def _parse_nested_table(self, table: Tag) -> Dict[str, Any]:
        rows = table.find_all("tr")
        if not rows:
            return {"headers": [], "rows": []}
        header_cells = rows[0].find_all(["th", "td"])
        headers = [clean_wiki_text(c.get_text(" ", strip=True)) for c in header_cells]
        data_rows: List[List[str]] = []
        for row in rows[1:]:
            cells = [clean_wiki_text(c.get_text(" ", strip=True)) for c in row.find_all(["th", "td"])]
            if cells:
                data_rows.append(cells)
        return {"headers": headers, "rows": data_rows}

    def _extract_links(self, cell: Tag) -> List[LinkRecord]:
        if not self.include_urls:
            return []
        return extract_links_from_cell(
            cell,
            full_url=lambda href: build_full_url(self.wikipedia_base, href),
            allow_local_anchors=False,
        )

    def _first_link(self, cell: Tag) -> LinkRecord | None:
        links = self._extract_links(cell)
        return links[0] if links else None

    def _extract_year_links(self, cell: Tag) -> List[LinkRecord]:
        links = [link for link in self._extract_links(cell) if self._is_year_link(link)]
        if links:
            return links

        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        years = re.findall(r"\b\d{4}(?:[-–]\d{4})?\b", text)
        return [{"text": year, "url": None} for year in years]

    @staticmethod
    def _is_year_link(link: LinkRecord) -> bool:
        text = link.get("text") or ""
        if not re.fullmatch(r"\d{4}(?:[-–]\d{4})?", text):
            return False
        url = (link.get("url") or "").lower()
        if "season" in url or "_season" in url:
            return False
        return True

    @staticmethod
    def _find_link_by_text(text: str, links: List[LinkRecord]) -> LinkRecord | None:
        wanted = text.strip().lower()
        for link in links:
            link_text = (link.get("text") or "").strip().lower()
            if link_text == wanted:
                return link
        return None
