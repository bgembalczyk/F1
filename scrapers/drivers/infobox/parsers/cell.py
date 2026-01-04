import re
from typing import Any
from typing import Dict
from typing import List

from bs4 import Tag

from models.services.helpers import parse_int_values
from models.services.helpers import parse_year_range
from models.services.helpers import split_delimited_text
from scrapers.base.errors import DomainParseError
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.drivers.infobox.parsers.link_extractor import InfoboxLinkExtractor


class InfoboxCellParser:
    def __init__(self, *, include_urls: bool, link_extractor: InfoboxLinkExtractor) -> None:
        self._include_urls = include_urls
        self._link_extractor = link_extractor

    def parse_cell(self, cell: Tag) -> Dict[str, Any]:
        text = clean_infobox_text(cell.get_text(" ", strip=True))
        payload = {"text": text}
        if self._include_urls:
            payload["links"] = self._link_extractor.extract_links(cell)
        return payload

    def parse_active_years(self, cell: Tag) -> List[Dict[str, Any]]:
        """Parse active years as a list of individual seasons with links.
        
        Handles cases like:
        - Individual years: 2002, 2005, 2007, 2008
        - Ranges: 2007-2008 (interpolates missing links)
        """
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        links = self._link_extractor.extract_links(cell)
        
        # Build a map of year -> link
        year_to_link: Dict[int, str | None] = {}
        for link in links:
            link_text = link.get("text", "")
            year_match = re.search(r'\b(\d{4})\b', link_text)
            if year_match:
                year = int(year_match.group(1))
                year_to_link[year] = link.get("url")
        
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
        if len(year_to_link) >= 2:
            # Detect URL pattern
            url_pattern = self._detect_url_pattern(year_to_link)
            if url_pattern:
                for year in years_set:
                    if year not in year_to_link:
                        year_to_link[year] = url_pattern.replace("{year}", str(year))
        
        # Build result list
        result = []
        for year in sorted(years_set):
            result.append({
                "year": year,
                "url": year_to_link.get(year)
            })
        
        return result
    
    @staticmethod
    def _detect_url_pattern(year_to_link: Dict[int, str | None]) -> str | None:
        """Detect a predictable URL pattern from available year links.
        
        Returns a pattern string with {year} placeholder if pattern is predictable.
        """
        urls = [(year, url) for year, url in year_to_link.items() if url]
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
    def _parse_year_range(text: str) -> Dict[str, int | None]:
        try:
            normalized = clean_infobox_text(text) or ""
            return parse_year_range(normalized)
        except (TypeError, ValueError) as exc:
            raise DomainParseError(
                f"Nie udało się sparsować zakresu lat: {text!r}.",
                cause=exc,
            ) from exc

    def parse_teams(self, cell: Tag) -> List[Any]:
        if self._include_urls:
            return self._link_extractor.extract_links(cell)
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        return split_delimited_text(text, pattern=r",")

    @staticmethod
    def parse_entries(cell: Tag) -> Dict[str, int | None]:
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        try:
            values = parse_int_values(text)
        except (TypeError, ValueError) as exc:
            raise DomainParseError(
                f"Nie udało się sparsować wpisów/startów: {text!r}.",
                cause=exc,
            ) from exc
        entries = values[0] if values else None
        starts = values[1] if len(values) > 1 else None
        return {"entries": entries, "starts": starts}

    @staticmethod
    def parse_int_cell(cell: Tag) -> int | None:
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        match = re.search(r"-?\d+", text.replace(",", ""))
        if not match:
            return None
        try:
            return int(match.group(0))
        except (TypeError, ValueError) as exc:
            raise DomainParseError(
                f"Nie udało się sparsować liczby całkowitej: {text!r}.",
                cause=exc,
            ) from exc

    @staticmethod
    def parse_float_cell(cell: Tag) -> float | None:
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        match = re.search(r"-?\d+(?:\.\d+)?", text.replace(",", ""))
        if not match:
            return None
        try:
            return float(match.group(0))
        except (TypeError, ValueError) as exc:
            raise DomainParseError(
                f"Nie udało się sparsować liczby zmiennoprzecinkowej: {text!r}.",
                cause=exc,
            ) from exc

    def parse_car_numbers(self, cell: Tag) -> List[Dict[str, Any]]:
        raw_text = cell.get_text("\n", strip=True) or ""
        if not raw_text:
            return []
        normalized = clean_wiki_text(raw_text, strip_lang_suffix=False)
        normalized = re.sub(r"\band\b", ",", normalized, flags=re.IGNORECASE)
        normalized = normalized.replace("/", ",").replace(";", ",")
        entries: List[Dict[str, Any]] = []
        pattern = re.compile(
            r"(?<!\d)(?P<prefix>No\.?|#|№)?\s*(?P<number>\d+)\s*(?:\((?P<years>[^)]+)\))?",
            re.IGNORECASE,
        )
        for match in pattern.finditer(normalized):
            prefix = match.group("prefix") or ""
            try:
                number = int(match.group("number"))
            except (TypeError, ValueError) as exc:
                raise DomainParseError(
                    f"Nie udało się sparsować numeru samochodu: {raw_text!r}.",
                    cause=exc,
                ) from exc
            if number >= 1900 and not prefix:
                continue
            years_text = match.group("years") or ""
            years = (
                self._parse_year_range(years_text)
                if years_text
                else {"start": None, "end": None}
            )
            entries.append({"number": number, "years": years})
        return entries

    def parse_best_finish(self, cell: Tag) -> Dict[str, Any]:
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        try:
            result: Dict[str, Any] = {"result": None, "season": None}
            
            # Extract result position (e.g., "1st", "4th")
            if " in " in text:
                result_text, _ = text.split(" in ", 1)
                result["result"] = result_text.strip() or None
            else:
                result["result"] = text.strip() or None
            
            # Extract season link
            links = self._link_extractor.extract_links(cell)
            season_links = [link for link in links if not self._is_class_link(link)]
            if season_links:
                season_link = season_links[0]
                # Extract year from link text
                year_match = re.search(r'\b(\d{4})(?:[-–](\d{2,4}))?\b', season_link.get("text", ""))
                if year_match:
                    year = int(year_match.group(1))
                    result["season"] = {
                        "year": year,
                        "url": season_link.get("url")
                    }
            
            # Extract class from <small> tag
            small_tag = cell.find("small")
            if small_tag:
                class_links = self._link_extractor.extract_links(small_tag)
                if class_links:
                    result["class"] = class_links[0]
            
            return result
        except (TypeError, ValueError) as exc:
            raise DomainParseError(
                f"Nie udało się sparsować najlepszego wyniku: {text!r}.",
                cause=exc,
            ) from exc
    
    @staticmethod
    def _is_class_link(link: LinkRecord) -> bool:
        """Check if link is a class designation (e.g., LMP1) rather than a season."""
        url = (link.get("url") or "").lower()
        text = (link.get("text") or "").upper()
        # Class links typically don't contain years or season references
        if "season" in url or "_season" in url:
            return False
        if re.search(r'\d{4}', text):
            return False
        return True

    def parse_full_data(self, cell: Tag) -> Dict[str, Any]:
        text = clean_infobox_text(cell.get_text(" ", strip=True))
        payload: Dict[str, Any] = {"text": text}
        if self._include_urls:
            payload["links"] = self._link_extractor.extract_links(cell)

        nested_table = cell.find("table")
        if nested_table:
            payload["table"] = self.parse_nested_table(nested_table)
        return payload

    @staticmethod
    def parse_nested_table(table: Tag) -> Dict[str, Any]:
        rows = table.find_all("tr")
        if not rows:
            return {"headers": [], "rows": []}
        header_cells = rows[0].find_all(["th", "td"])
        headers = [clean_wiki_text(c.get_text(" ", strip=True)) for c in header_cells]
        data_rows: List[List[str]] = []
        for row in rows[1:]:
            cells = [
                clean_wiki_text(c.get_text(" ", strip=True))
                for c in row.find_all(["th", "td"])
            ]
            if cells:
                data_rows.append(cells)
        return {"headers": headers, "rows": data_rows}
