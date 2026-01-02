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

            title_links = self._extract_title_links(value_cell)
            year_links = self._extract_year_links(label_cell)

            if title_links and year_links and len(title_links) == len(year_links) and len(title_links) > 1:
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
            titles.append({"title": {"text": title_text or "", "url": None}, "years": year_links})

        return titles

    def _parse_career_section(self, title: str, section: Dict[str, Any]) -> Dict[str, Any]:
        rows: List[Dict[str, Any]] = []
        for row in section.get("rows", []):
            if "label_cell" in row and "value_cell" in row:
                label_cell = row["label_cell"]
                value_cell = row["value_cell"]
                label = clean_infobox_text(label_cell.get_text(" ", strip=True))
                if label in {"Active years", "Years active"}:
                    value = self._parse_active_years(value_cell)
                elif label == "Car number":
                    value = self._parse_car_numbers(value_cell)
                elif label == "Teams":
                    value = self._parse_teams(value_cell)
                elif label == "Entries":
                    value = self._parse_entries(value_cell)
                elif label in {"Wins", "Podiums", "Pole positions", "Fastest laps", "Starts"}:
                    value = self._parse_int_cell(value_cell)
                elif label == "Career points":
                    value = self._parse_float_cell(value_cell)
                elif label == "Best finish":
                    value = self._parse_best_finish(value_cell)
                else:
                    value = self._parse_cell(value_cell)
                rows.append(
                    {
                        "label": label,
                        "value": value,
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
            series_links = self._extract_title_links(value_cell)
            year_links = self._extract_year_links(label_cell)
            if series_links and year_links and len(series_links) == len(year_links) and len(series_links) > 1:
                for series_link, year_link in zip(series_links, year_links):
                    items.append({"title": series_link, "years": [year_link]})
                continue
            if series_links and year_links:
                items.append({"title": series_links[0], "years": year_links})
                continue
            if series_links:
                for series_link in series_links:
                    items.append({"title": series_link, "years": []})
                continue
            series_text = clean_infobox_text(value_cell.get_text(" ", strip=True))
            items.append({"title": {"text": series_text or "", "url": None}, "years": year_links})
        return items

    def _parse_cell(self, cell: Tag) -> Dict[str, Any]:
        text = clean_infobox_text(cell.get_text(" ", strip=True))
        payload = {"text": text}
        if self.include_urls:
            payload["links"] = self._extract_links(cell)
        return payload

    def _parse_active_years(self, cell: Tag) -> Dict[str, int | None]:
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        return self._parse_year_range(text)

    def _parse_year_range(self, text: str) -> Dict[str, int | None]:
        normalized = clean_infobox_text(text) or ""
        range_match = re.search(r"\b(\d{4})\s*[-–]\s*(\d{2,4})\b", normalized)
        if range_match:
            start = int(range_match.group(1))
            end_text = range_match.group(2)
            if len(end_text) == 2:
                end = (start // 100) * 100 + int(end_text)
            else:
                end = int(end_text)
            return {"start": start, "end": end}

        years = [int(value) for value in re.findall(r"\d{4}", normalized)]
        if not years:
            return {"start": None, "end": None}
        start = years[0]
        if "present" in normalized.lower() and len(years) == 1:
            end = None
        elif len(years) > 1:
            end = years[-1]
        else:
            end = start
        return {"start": start, "end": end}

    def _parse_teams(self, cell: Tag) -> List[Any]:
        if self.include_urls:
            return self._extract_links(cell)
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        if not text:
            return []
        return [part for part in (p.strip() for p in text.split(",")) if part]

    def _parse_entries(self, cell: Tag) -> Dict[str, int | None]:
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        values = [int(value) for value in re.findall(r"\d+", text)]
        entries = values[0] if values else None
        starts = values[1] if len(values) > 1 else None
        return {"entries": entries, "starts": starts}

    def _parse_int_cell(self, cell: Tag) -> int | None:
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        match = re.search(r"-?\d+", text.replace(",", ""))
        return int(match.group(0)) if match else None

    def _parse_float_cell(self, cell: Tag) -> float | None:
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        match = re.search(r"-?\d+(?:\.\d+)?", text.replace(",", ""))
        return float(match.group(0)) if match else None

    def _parse_car_numbers(self, cell: Tag) -> List[Dict[str, Any]]:
        text = clean_infobox_text(cell.get_text("\n", strip=True)) or ""
        entries: List[Dict[str, Any]] = []
        for part in (line.strip() for line in text.splitlines() if line.strip()):
            match = re.match(r"^(?P<number>\d+)\s*(?:\((?P<years>[^)]+)\))?$", part)
            if not match:
                continue
            number = int(match.group("number"))
            years_text = match.group("years") or ""
            years = self._parse_year_range(years_text) if years_text else {"start": None, "end": None}
            entries.append({"number": number, "years": years})
        return entries

    def _parse_best_finish(self, cell: Tag) -> Dict[str, Any]:
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        if " in " in text:
            result_text, season_text = text.split(" in ", 1)
            season = self._parse_year_range(season_text)
        else:
            result_text = text
            season = {"start": None, "end": None}
        return {"result": result_text.strip() or None, "season": season}

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

    def _extract_title_links(self, cell: Tag) -> List[LinkRecord]:
        links = self._extract_links(cell)
        if links:
            return links
        text = clean_infobox_text(cell.get_text("\n", strip=True)) or ""
        parts = [part.strip() for part in text.split("\n") if part.strip()]
        return [{"text": part, "url": None} for part in parts]

    def _extract_year_links(self, cell: Tag) -> List[LinkRecord]:
        links = [link for link in self._extract_links(cell) if self._is_year_link(link)]
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
