import re
from typing import Any
from typing import Dict
from typing import List

from bs4 import BeautifulSoup
from bs4 import Tag

from models.records.link import LinkRecord
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
        """Parse year range from text.
        
        Handles cases like:
        - "2018-2022" -> {start: 2018, end: 2022}
        - "2018-19–2022" -> {start: 2018, end: 2022}  # Multiple dashes
        - "2018" -> {start: 2018, end: 2018}
        - "2015–present" -> {start: 2015, end: None}
        """
        try:
            normalized = clean_infobox_text(text) or ""
            
            # Check for "present" keyword
            has_present = re.search(r'\bpresent\b', normalized, re.IGNORECASE) is not None
            
            # Extract all 4-digit years and 2-digit years
            all_years = []
            
            # Find all standalone 4-digit years
            four_digit_years = [int(y) for y in re.findall(r'\b(\d{4})\b', normalized)]
            all_years.extend(four_digit_years)
            
            # Find 2-digit years that come after 4-digit years (like "2018-19")
            two_digit_pattern = re.finditer(r'\b(\d{4})\s*[-–]\s*(\d{2})\b', normalized)
            for match in two_digit_pattern:
                start_year = int(match.group(1))
                end_suffix = match.group(2)
                end_year = (start_year // 100) * 100 + int(end_suffix)
                if end_year not in all_years:
                    all_years.append(end_year)
            
            if not all_years:
                return {"start": None, "end": None}
            
            # Sort years and take first and last
            all_years.sort()
            start = all_years[0]
            # If "present" is in text, end should be None
            end = None if has_present else all_years[-1]
            
            return {"start": start, "end": end}
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
    
    def parse_championships(self, cell: Tag) -> Dict[str, Any]:
        """Parse championships count with links.
        
        Handles cases like:
        - "1 (2014)" -> {count: 1, championships: [{text: "2014", url: ...}]}
        - "2 (2015, 2016)" -> {count: 2, championships: [{text: "2015", url: ...}, {text: "2016", url: ...}]}
        """
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        try:
            # Extract count
            count_match = re.search(r"^(\d+)", text)
            count = int(count_match.group(1)) if count_match else 0
            
            # Extract links from parentheses - treat as simple list of links
            championships = self._link_extractor.extract_links(cell)
            
            return {
                "count": count,
                "championships": championships
            }
        except (TypeError, ValueError) as exc:
            raise DomainParseError(
                f"Nie udało się sparsować mistrzostw: {text!r}.",
                cause=exc,
            ) from exc
    
    def parse_class_wins(self, cell: Tag) -> Dict[str, Any]:
        """Parse class wins count with year and link information.
        
        Similar to championships, handles cases like:
        - "6 (1969, 1975, 1976)" -> {count: 6, wins: [{year: 1969, url: ...}, ...]}
        """
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        try:
            # Extract count
            count_match = re.search(r"^(\d+)", text)
            count = int(count_match.group(1)) if count_match else 0
            
            # Extract year links
            wins = []
            links = self._link_extractor.extract_links(cell)
            
            # Build year -> url mapping from links
            year_to_url: Dict[int, str | None] = {}
            for link in links:
                link_text = link.get("text", "")
                year_match = re.search(r'\b(\d{4})\b', link_text)
                if year_match:
                    year = int(year_match.group(1))
                    year_to_url[year] = link.get("url")
            
            # Extract all years from text (typically in parentheses or <small> tag)
            # Check <small> tag first
            small_tag = cell.find("small")
            if small_tag:
                small_text = clean_infobox_text(small_tag.get_text(" ", strip=True)) or ""
                for year_match in re.finditer(r'\b(\d{4})\b', small_text):
                    year = int(year_match.group(1))
                    wins.append({
                        "year": year,
                        "url": year_to_url.get(year)
                    })
            else:
                # Fallback to extracting from parentheses in main text
                paren_match = re.search(r'\(([^)]+)\)', text)
                if paren_match:
                    paren_content = paren_match.group(1)
                    for year_match in re.finditer(r'\b(\d{4})\b', paren_content):
                        year = int(year_match.group(1))
                        wins.append({
                            "year": year,
                            "url": year_to_url.get(year)
                        })
            
            return {
                "count": count,
                "wins": wins
            }
        except (TypeError, ValueError) as exc:
            raise DomainParseError(
                f"Nie udało się sparsować zwycięstw klasowych: {text!r}.",
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
            result: Dict[str, Any] = {"result": None, "seasons": None}
            
            # Extract result position (e.g., "1st", "4th", "6th")
            if " in " in text:
                result_text, _ = text.split(" in ", 1)
                result["result"] = result_text.strip() or None
            else:
                # Extract result without parentheses content
                result_match = re.match(r'^([^(]+)', text)
                if result_match:
                    result["result"] = result_match.group(1).strip() or None
                else:
                    result["result"] = text.strip() or None
            
            # Extract season links and small tags (classes) together
            # Pattern: "1st in 2019–20 (LMP1), 2021 (LMH)"
            # We need to pair each season with its corresponding class if present
            
            links = self._link_extractor.extract_links(cell)
            season_links = [link for link in links if not self._is_class_link(link)]
            
            if season_links:
                # Find all <small> tags that might contain class info
                small_tags = cell.find_all("small")
                
                # Build a map of season positions to class links
                # We'll match based on proximity/order in the HTML
                season_data = []
                
                if small_tags and len(small_tags) > 0:
                    # Parse HTML to find season-class pairs
                    # Strategy: find each season link, then look for the next <small> tag
                    cell_html = str(cell)
                    
                    # For each season link, try to find associated class
                    for season_link in season_links:
                        season_entry = {
                            "text": season_link.get("text", ""),
                            "url": season_link.get("url")
                        }
                        
                        # Find the season text in the HTML
                        season_text = season_link.get("text", "")
                        if season_text:
                            # Look for <small> tag that comes after this season
                            season_pos = cell_html.find(f'>{season_text}<')
                            if season_pos == -1:
                                season_pos = cell_html.find(season_text)
                            
                            if season_pos >= 0:
                                # Find the next <small> tag after this position
                                small_start = cell_html.find('<small', season_pos)
                                if small_start >= 0:
                                    small_end = cell_html.find('</small>', small_start)
                                    if small_end >= 0:
                                        # Check if there's another season link before this small tag
                                        next_season_pos = len(cell_html)
                                        for other_season in season_links:
                                            if other_season != season_link:
                                                other_text = other_season.get("text", "")
                                                other_pos = cell_html.find(other_text, season_pos + len(season_text))
                                                if season_pos < other_pos < small_start:
                                                    next_season_pos = other_pos
                                                    break
                                        
                                        # Only associate if small tag is before next season
                                        if small_start < next_season_pos:
                                            # Extract class link from this small tag
                                            small_html = cell_html[small_start:small_end + 8]
                                            small_soup = BeautifulSoup(small_html, 'html.parser')
                                            small_tag_obj = small_soup.find('small')
                                            if small_tag_obj:
                                                class_links = self._link_extractor.extract_links(small_tag_obj)
                                                if class_links:
                                                    season_entry["class"] = class_links[0]
                        
                        season_data.append(season_entry)
                    
                    result["seasons"] = season_data
                else:
                    # No small tags, just return seasons
                    result["seasons"] = [
                        {
                            "text": link.get("text", ""),
                            "url": link.get("url")
                        }
                        for link in season_links
                    ]
            else:
                # No links - try to extract years from parentheses
                paren_match = re.search(r'\(([^)]+)\)', text)
                if paren_match:
                    paren_content = paren_match.group(1)
                    # Extract all years
                    years = [int(y) for y in re.findall(r'\b(\d{4})\b', paren_content)]
                    if years:
                        result["seasons"] = years
            
            
            return result
        except (TypeError, ValueError) as exc:
            raise DomainParseError(
                f"Nie udało się sparsować najlepszego wyniku: {text!r}.",
                cause=exc,
            ) from exc
    
    def parse_race_event(self, cell: Tag) -> List[Dict[str, Any]]:
        """Parse race event fields like First race, Last race, First win, Last win, First entry, Last entry.
        
        Returns a list of all links found in the cell.
        If no links are found, returns the text as a single-item list with text field.
        """
        try:
            links = self._link_extractor.extract_links(cell)
            
            # If we have links, return them
            if links:
                return links
            
            # If no links, return the text
            text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
            if text:
                return [{"text": text, "url": None}]
            
            return []
        except (TypeError, ValueError) as exc:
            text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
            raise DomainParseError(
                f"Nie udało się sparsować wydarzenia wyścigowego: {text!r}.",
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
    
    def parse_finished_last_season(self, cell: Tag) -> Dict[str, Any]:
        """Parse 'Finished last season' field.
        
        Example: "14th (62 pts)" -> {position: "14th", points: 62}
        """
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        try:
            result: Dict[str, Any] = {"position": None, "points": None}
            
            # Extract position (before parentheses)
            pos_match = re.match(r'^([^(]+)', text)
            if pos_match:
                result["position"] = pos_match.group(1).strip() or None
            
            # Extract points from parentheses
            pts_match = re.search(r'\((\d+(?:\.\d+)?)\s*pts?\)', text)
            if pts_match:
                points_str = pts_match.group(1)
                try:
                    # Try parsing as int first
                    result["points"] = int(points_str)
                except ValueError:
                    # Fall back to float
                    result["points"] = float(points_str)
            
            return result
        except (TypeError, ValueError) as exc:
            raise DomainParseError(
                f"Nie udało się sparsować ostatniego sezonu: {text!r}.",
                cause=exc,
            ) from exc
    
    def parse_racing_licence(self, cell: Tag) -> List[Dict[str, Any]]:
        """Parse 'Racing licence' field.
        
        Example: "FIA Gold (until 2019)" and "FIA Platinum (2020–)" 
        -> [{licence: {...}, years: {start: None, end: 2019}}, {licence: {...}, years: {start: 2020, end: None}}]
        """
        try:
            # Extract all links from the cell first
            all_links = self._link_extractor.extract_links(cell)
            
            # Split by <br> tags to get separate licence entries
            # Create a copy to avoid modifying the original
            cell_copy = BeautifulSoup(str(cell), 'html.parser')
            for br in cell_copy.find_all('br'):
                br.replace_with('\n')
            
            text = cell_copy.get_text('\n', strip=True)
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            licences = []
            link_index = 0  # Track which link we're processing
            
            for line in lines:
                # Skip lines that don't contain links or are just references
                if not any(link.get('text', '') in line for link in all_links[link_index:]):
                    continue
                
                # Find the link for this line
                licence_link = None
                for i, link in enumerate(all_links[link_index:], start=link_index):
                    if link.get('text', '') in line:
                        licence_link = link
                        link_index = i + 1
                        break
                
                if not licence_link:
                    continue
                
                # Extract year range from parentheses
                years: Dict[str, int | None] = {"start": None, "end": None}
                paren_match = re.search(r'\(([^)]+)\)', line)
                if paren_match:
                    year_text = paren_match.group(1)
                    
                    # Handle "until YEAR"
                    if "until" in year_text.lower():
                        year_match = re.search(r'\b(\d{4})\b', year_text)
                        if year_match:
                            years["end"] = int(year_match.group(1))
                    # Handle "YEAR–" or "YEAR–present"
                    elif re.search(r'\b(\d{4})\s*[–-]\s*(?:present)?$', year_text):
                        year_match = re.search(r'\b(\d{4})\b', year_text)
                        if year_match:
                            years["start"] = int(year_match.group(1))
                    # Handle "YEAR–YEAR"
                    else:
                        years = self._parse_year_range(year_text)
                
                licences.append({
                    "licence": licence_link,
                    "years": years
                })
            
            return licences
        except (TypeError, ValueError) as exc:
            text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
            raise DomainParseError(
                f"Nie udało się sparsować licencji wyścigowej: {text!r}.",
                cause=exc,
            ) from exc

    def parse_full_data(self, cell: Tag) -> Dict[str, Any]:
        text = clean_infobox_text(cell.get_text(" ", strip=True))
        
        nested_table = cell.find("table")
        if nested_table:
            table_data = self.parse_nested_table(nested_table)
            # Check if this is a Wins/Podiums/Poles table
            if self._is_stats_table(table_data):
                # Extract the values directly and return only stats
                stats = self._extract_stats_from_table(table_data)
                return stats
            else:
                # For other tables, include full metadata
                payload: Dict[str, Any] = {"text": text}
                if self._include_urls:
                    payload["links"] = self._link_extractor.extract_links(cell)
                payload["table"] = table_data
                return payload
        
        # Check if this is "X races run over Y years" pattern
        if text is not None:
            races_run_match = re.match(r'^(\d+)\s+races?\s+run\s+over', text)
            if races_run_match:
                return {"races_run": int(races_run_match.group(1))}
        
        # Default: return text and links
        payload: Dict[str, Any] = {"text": text}
        if self._include_urls:
            payload["links"] = self._link_extractor.extract_links(cell)
        return payload
    
    @staticmethod
    def _is_stats_table(table_data: Dict[str, Any]) -> bool:
        """Check if table is a Wins/Podiums/Poles stats table."""
        headers = table_data.get("headers", [])
        if len(headers) != 3:
            return False
        # Normalize headers for comparison
        normalized = [h.lower().strip() for h in headers]
        expected = ["wins", "podiums", "poles"]
        return normalized == expected
    
    @staticmethod
    def _extract_stats_from_table(table_data: Dict[str, Any]) -> Dict[str, int | None]:
        """Extract Wins, Podiums, Poles from stats table."""
        stats: Dict[str, int | None] = {
            "wins": None,
            "podiums": None,
            "poles": None
        }
        rows = table_data.get("rows", [])
        if rows and len(rows[0]) >= 3:
            # First row contains the values
            try:
                stats["wins"] = int(rows[0][0])
            except (ValueError, IndexError):
                pass
            try:
                stats["podiums"] = int(rows[0][1])
            except (ValueError, IndexError):
                pass
            try:
                stats["poles"] = int(rows[0][2])
            except (ValueError, IndexError):
                pass
        return stats

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
