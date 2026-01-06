# TODO: Ta klasa jest dość duża; rozważ podział na mniejsze klasy lub moduły, jeśli to możliwe.

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
    # Regex patterns for year detection (compiled once for performance)
    _FOUR_DIGIT_YEAR_PATTERN = re.compile(r'^(19|20)\d{2}$')
    _TWO_DIGIT_SUFFIX_PATTERN = re.compile(r'^\d{2}$')
    
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
            
            # Extract season links and class information from small tags
            links = self._link_extractor.extract_links(cell)
            season_links = [link for link in links if not self._is_class_link(link)]
            
            if season_links:
                # Find all <small> tags that might contain class info
                small_tags = cell.find_all("small")
                
                season_data = []
                
                if small_tags:
                    # Determine if we have one class for all seasons or one class per season
                    # by counting how many <small> tags exist
                    num_small_tags = len(small_tags)
                    num_seasons = len(season_links)
                    
                    if num_small_tags == 1:
                        # Single class applies to all seasons
                        class_links = self._link_extractor.extract_links(small_tags[0])
                        class_info = class_links[0] if class_links else None
                        
                        # Validate that class_info is actually a class, not season data
                        if not self._is_valid_class_info(class_info, season_links):
                            class_info = None
                        
                        for season_link in season_links:
                            season_entry = {
                                "text": season_link.get("text", ""),
                                "url": season_link.get("url")
                            }
                            if class_info:
                                season_entry["class"] = class_info
                            season_data.append(season_entry)
                    else:
                        # Multiple small tags - match each season to its nearest small tag
                        for season_link in season_links:
                            season_entry = {
                                "text": season_link.get("text", ""),
                                "url": season_link.get("url")
                            }
                            
                            # Find the actual <a> tag in the cell that matches this season
                            season_text = season_link.get("text", "")
                            season_url = season_link.get("url", "")
                            
                            if season_text:
                                # Find the <a> tag with this text
                                season_tag = None
                                for a_tag in cell.find_all('a'):
                                    if clean_infobox_text(a_tag.get_text(strip=True)) == season_text:
                                        # Verify URL matches if present
                                        # season_url is a full URL, a_href is relative
                                        a_href = a_tag.get('href', '') or ''
                                        if not season_url or a_href in season_url:
                                            season_tag = a_tag
                                            break
                                
                                # Look for next <small> tag after this season tag
                                if season_tag:
                                    # Navigate forward to find next small tag
                                    next_elem = season_tag
                                    found_small = None
                                    found_next_season = False
                                    
                                    # Search through next siblings
                                    while next_elem and not found_small and not found_next_season:
                                        next_elem = next_elem.next_sibling
                                        if next_elem:
                                            # Check if next_elem is a Tag before calling find_all
                                            if hasattr(next_elem, 'name'):
                                                if next_elem.name == 'small':
                                                    found_small = next_elem
                                                    break
                                                # Check if we hit another season link
                                                if next_elem.name == 'a':
                                                    next_text = clean_infobox_text(next_elem.get_text(strip=True))
                                                    if any(s.get("text") == next_text for s in season_links if s != season_link):
                                                        found_next_season = True
                                                        break
                                            # Also search descendants of text/tag siblings
                                            if isinstance(next_elem, Tag):
                                                small_in_sibling = next_elem.find('small')
                                                if small_in_sibling:
                                                    # Check if there's a season link before this small
                                                    for a_tag in next_elem.find_all('a'):
                                                        a_text = clean_infobox_text(a_tag.get_text(strip=True))
                                                        if any(s.get("text") == a_text for s in season_links if s != season_link):
                                                            found_next_season = True
                                                            break
                                                    if not found_next_season:
                                                        found_small = small_in_sibling
                                                        break
                                    
                                    # Extract class from found small tag
                                    if found_small:
                                        class_links = self._link_extractor.extract_links(found_small)
                                        if class_links:
                                            class_candidate = class_links[0]
                                            class_text = class_candidate.get("text", "")
                                            class_url = class_candidate.get("url", "")
                                            
                                            # Validate that this is actually a class, not season data
                                            # Check if it looks like season data (years only)
                                            is_valid = not self._is_season_like_text(class_text)
                                            # Check if it duplicates the current season
                                            if is_valid and (season_text == class_text or season_url == class_url):
                                                is_valid = False
                                            
                                            if is_valid:
                                                season_entry["class"] = class_candidate
                            
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
                # No links - try to extract years from text
                # Pattern 1: "1st in 1957" -> extract years after "in"
                # Pattern 2: "1st in 1952, 1954" -> extract comma-separated years
                if " in " in text:
                    # Extract text after "in"
                    _, years_text = text.split(" in ", 1)
                    # Remove any parenthetical content
                    years_text = re.sub(r'\s*\([^)]*\)', '', years_text).strip()
                    # Extract all years from the text
                    years = [int(y) for y in re.findall(r'\b(\d{4})\b', years_text)]
                    if years:
                        result["seasons"] = years
                else:
                    # Try to find years in parentheses
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
    
    def _is_valid_class_info(
        self, 
        class_info: Dict[str, Any], 
        season_links: List[Dict[str, Any]]
    ) -> bool:
        """Check if class_info is valid (not season data and not a duplicate).
        
        Args:
            class_info: The potential class information to validate
            season_links: List of season links to check for duplicates
            
        Returns:
            True if class_info is a valid class, False if it's season data or a duplicate
        """
        if not class_info:
            return False
        
        class_text = class_info.get("text", "")
        class_url = class_info.get("url", "")
        
        # Check if class looks like season data (years only)
        if self._is_season_like_text(class_text):
            return False
        
        # Check if class duplicates any season
        for season_link in season_links:
            if season_link.get("text") == class_text or season_link.get("url") == class_url:
                return False
        
        return True
    
    def _is_season_like_text(self, text: str) -> bool:
        """Check if text looks like season data (years) rather than a class name.
        
        Season-like text contains only years and separators:
        - Single years: "2013", "2014"
        - Year ranges with 2-digit suffix: "2013-14", "2019–20" (where "14" means 2014, "20" means 2020)
        - Full year ranges: "2013-2014", "2013–2014"
        - Multiple years: "2013, 2014, 2015"
        - Combinations: "2013-2015, 2018"
        
        Class names typically contain letters (possibly with numbers) in non-year format.
        Examples of class names: "LMP1", "LMH", "LMP2", "GT3", "LMP2-H"
        
        Args:
            text: The text to check
            
        Returns:
            True if the text looks like season/year data, False if it looks like a class name
        """
        if not text:
            return False
        
        # Remove common separators and whitespace to get individual parts
        cleaned = text.replace(',', ' ').replace('–', ' ').replace('-', ' ')
        parts = cleaned.split()
        
        if not parts:
            return False
        
        # Check if all parts are either 4-digit years or 2-digit year suffixes
        # and ensure at least one 4-digit year is present
        has_four_digit_year = False
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            if self._FOUR_DIGIT_YEAR_PATTERN.match(part):
                # It's a 4-digit year (1900-2099)
                has_four_digit_year = True
            elif self._TWO_DIGIT_SUFFIX_PATTERN.match(part):
                # It's a 2-digit suffix (00-99)
                # These are only valid when combined with 4-digit years (like "2019-20")
                pass
            else:
                # Not a year or suffix - likely a class name with letters
                return False
        
        # Valid season-like text must have at least one 4-digit year
        # 2-digit suffixes alone (like "20") are not sufficient
        return has_four_digit_year
    
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
            # Extract all links from the cell first, filtering out image/file links
            all_links = self._link_extractor.extract_links(cell)
            # Filter out links to files (images, etc.) - they typically contain "File:" in URL
            licence_links = [link for link in all_links if not (link.get('url', '').lower().find('/file:') >= 0)]
            
            if not licence_links:
                return []
            
            # Find all <span> tags with year information (font-size styling)
            year_spans = cell.find_all('span', style=lambda x: x and 'font-size' in x)
            
            licences = []
            
            # Strategy: For each licence link, find the nearest year span that comes after it
            for licence_link in licence_links:
                licence_entry = {
                    "licence": licence_link,
                    "years": {"start": None, "end": None}
                }
                
                # Find the actual <a> tag for this licence in the cell
                licence_text = licence_link.get('text', '')
                licence_url = licence_link.get('url', '')
                
                licence_tag = None
                for a_tag in cell.find_all('a'):
                    if clean_infobox_text(a_tag.get_text(strip=True)) == licence_text:
                        # Verify URL matches if present
                        # licence_url is a full URL, a_href is relative
                        a_href = a_tag.get('href', '') or ''
                        if not licence_url or a_href in licence_url:
                            # Make sure this is not a file/image link
                            if '/file:' not in a_href.lower():
                                licence_tag = a_tag
                                break
                
                # Look for the next year span after this licence tag
                if licence_tag and year_spans:
                    # Cache all <a> tags once to avoid repeated find_all calls
                    all_a_tags = cell.find_all('a')
                    
                    # Build a map of licence text -> tag for efficient lookup
                    licence_tag_map = {}
                    for other_link in licence_links:
                        if other_link == licence_link:
                            continue
                        other_text = other_link.get('text', '')
                        if other_text and other_text not in licence_tag_map:
                            for a_tag in all_a_tags:
                                if clean_infobox_text(a_tag.get_text(strip=True)) == other_text:
                                    a_href = a_tag.get('href', '') or ''
                                    if '/file:' not in a_href.lower():
                                        licence_tag_map[other_text] = a_tag
                                        break
                    
                    # Find which year span comes after this licence tag
                    for year_span in year_spans:
                        # Check if this span comes after the licence tag in the document order
                        if self._is_element_before(licence_tag, year_span):
                            # This span is after the licence tag
                            # Check if there's another licence link between them
                            has_licence_between = False
                            for other_tag in licence_tag_map.values():
                                # Check if this other licence is between current licence and year span
                                if self._is_element_before(licence_tag, other_tag) and self._is_element_before(other_tag, year_span):
                                    has_licence_between = True
                                    break
                            
                            if not has_licence_between:
                                # This year span belongs to this licence
                                year_text = year_span.get_text(strip=True)
                                licence_entry["years"] = self._parse_licence_years(year_text)
                                break
                
                licences.append(licence_entry)
            
            return licences
        except (TypeError, ValueError) as exc:
            text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
            raise DomainParseError(
                f"Nie udało się sparsować licencji wyścigowej: {text!r}.",
                cause=exc,
            ) from exc
    
    @staticmethod
    def _is_element_before(elem1: Tag, elem2: Tag) -> bool:
        """Check if elem1 comes before elem2 in document order.
        
        Uses BeautifulSoup's built-in ordering to compare positions efficiently.
        """
        # Get all elements in order by traversing once
        # Find the first occurrence - if it's elem1, then elem1 is before elem2
        elem1_parents = list(elem1.parents)
        elem2_parents = list(elem2.parents)
        
        # Find deepest common parent
        common_parent = None
        for p1 in elem1_parents:
            if p1 in elem2_parents:
                common_parent = p1
                break
        
        if common_parent is None:
            return False
        
        # Use BeautifulSoup's generator to avoid creating a full list
        for descendant in common_parent.descendants:
            if descendant is elem1:
                return True
            if descendant is elem2:
                return False
        
        return False
    
    @staticmethod
    def _parse_licence_years(year_text: str) -> Dict[str, int | None]:
        """Parse year information from licence year text.
        
        Handles formats like:
        - "(until 2019)" -> {start: None, end: 2019}
        - "(2020–)" -> {start: 2020, end: None}
        - "(2015-2018)" -> {start: 2015, end: 2018}
        """
        years: Dict[str, int | None] = {"start": None, "end": None}
        
        # Remove parentheses if present
        year_text = year_text.strip('()')
        
        # Handle "until YEAR"
        if "until" in year_text.lower():
            year_match = re.search(r'\b(\d{4})\b', year_text)
            if year_match:
                years["end"] = int(year_match.group(1))
        # Handle "YEAR–" or "YEAR-" (open-ended, possibly with "present")
        elif re.search(r'\b(\d{4})\s*[–-]\s*(?:present)?$', year_text.strip()):
            year_match = re.search(r'\b(\d{4})\b', year_text)
            if year_match:
                years["start"] = int(year_match.group(1))
        # Handle "YEAR–YEAR" or "YEAR-YEAR"
        else:
            all_years = re.findall(r'\b(\d{4})\b', year_text)
            if len(all_years) >= 2:
                years["start"] = int(all_years[0])
                years["end"] = int(all_years[-1])
            elif len(all_years) == 1:
                # Single year without context (e.g., just "(2015)")
                # Treat as a single-year validity period (both start and end are the same)
                # This is a reasonable assumption for racing licences that were valid only in one year
                years["start"] = int(all_years[0])
                years["end"] = int(all_years[0])
        
        return years

    def parse_full_data(self, cell: Tag) -> Dict[str, Any]:
        text = clean_infobox_text(cell.get_text(" ", strip=True))
        
        nested_table = cell.find("table")
        if nested_table:
            table_data = self.parse_nested_table(nested_table)
            # Check if this is a Wins/Podiums/Poles table or Wins/Top tens/Poles table
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
        # Only run regex if text is not None
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
        """Check if table is a Wins/Podiums/Poles or Wins/Top tens/Poles stats table."""
        headers = table_data.get("headers", [])
        if len(headers) != 3:
            return False
        # Normalize headers for comparison
        normalized = [h.lower().strip() for h in headers]
        expected_wins_podiums_poles = ["wins", "podiums", "poles"]
        expected_wins_topten_poles = ["wins", "top tens", "poles"]
        return normalized == expected_wins_podiums_poles or normalized == expected_wins_topten_poles
    
    @staticmethod
    def _extract_stats_from_table(table_data: Dict[str, Any]) -> Dict[str, int | None]:
        """Extract Wins, Podiums/Top tens, Poles from stats table."""
        headers = table_data.get("headers", [])
        normalized = [h.lower().strip() for h in headers]
        
        stats: Dict[str, int | None] = {
            "wins": None,
            "podiums": None,
            "top_tens": None,
            "poles": None
        }
        rows = table_data.get("rows", [])
        if rows and len(rows[0]) >= 3:
            # First row contains the values
            # Determine if we have podiums or top tens based on header
            has_podiums = "podiums" in normalized
            has_top_tens = "top tens" in normalized
            
            try:
                stats["wins"] = int(rows[0][0])
            except (ValueError, IndexError):
                pass
            
            # Second column is either podiums or top tens
            if has_podiums:
                try:
                    stats["podiums"] = int(rows[0][1])
                except (ValueError, IndexError):
                    pass
            elif has_top_tens:
                try:
                    stats["top_tens"] = int(rows[0][1])
                except (ValueError, IndexError):
                    pass
            
            try:
                stats["poles"] = int(rows[0][2])
            except (ValueError, IndexError):
                pass
        
        # Remove None values for cleaner output
        return {k: v for k, v in stats.items() if v is not None}

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
    
    def parse_nationality(self, cell: Tag) -> List[str] | List[Dict[str, Any]]:
        """Parse nationality field.
        
        Handles cases like:
        - "American or Italian" -> ["American", "Italian"]
        - "Federation of Rhodesia and Nyasaland (1963)" with year ranges -> structured data
        """
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        
        # Check if there are year references (indicating nationality changed by season)
        has_years = re.search(r'\(\s*\d{4}', text)
        
        if has_years:
            # Parse structured nationality with years
            # Split by <br> tags to separate different nationalities
            br_parts = []
            html = str(cell)
            parts = re.split(r'<br\s*/?>', html, flags=re.IGNORECASE)
            
            nationalities = []
            
            for part_html in parts:
                if not part_html.strip():
                    continue
                
                # Parse this part
                part_soup = BeautifulSoup(part_html, 'html.parser')
                part_text = clean_infobox_text(part_soup.get_text(" ", strip=True)) or ""
                
                # Extract nationality name (before any year information)
                # Pattern: "Nationality_name (year)" or "Nationality_name (year, year-year)"
                # Remove year information to get nationality name
                nationality_name = re.sub(r'\s*\([^)]*\d{4}[^)]*\)', '', part_text).strip()
                
                # Extract all year patterns from this part
                # Look for individual years and year ranges in <small> tags or parentheses
                years = []
                
                # Find all year patterns in text
                # Pattern 1: (1963) -> single year
                # Pattern 2: (1965, 1967-1968) -> multiple years and ranges
                year_patterns = re.findall(r'\(([^)]*\d{4}[^)]*)\)', part_text)
                
                for year_pattern in year_patterns:
                    # Extract individual years and ranges
                    # Find ranges first
                    for range_match in re.finditer(r'(\d{4})\s*[-–]\s*(\d{4})', year_pattern):
                        start = int(range_match.group(1))
                        end = int(range_match.group(2))
                        for year in range(start, end + 1):
                            if year not in years:
                                years.append(year)
                    
                    # Find individual years
                    for year_match in re.finditer(r'\b(\d{4})\b', year_pattern):
                        year = int(year_match.group(1))
                        if year not in years:
                            years.append(year)
                
                if nationality_name and years:
                    nationalities.append({
                        "nationality": nationality_name,
                        "years": sorted(years)
                    })
                elif nationality_name:
                    # Nationality without specific years
                    nationalities.append({
                        "nationality": nationality_name,
                        "years": []
                    })
            
            return nationalities if nationalities else []
        else:
            # Simple case: just extract nationality names separated by "or"
            # Split by "or" to get multiple nationalities
            parts = re.split(r'\s+or\s+', text, flags=re.IGNORECASE)
            nationalities = []
            
            for part in parts:
                # Clean up each part
                part = part.strip()
                # Remove any reference markers like [1]
                part = re.sub(r'\[\d+\]', '', part).strip()
                if part:
                    nationalities.append(part)
            
            return nationalities if len(nationalities) > 1 else (nationalities or [])
    
    def parse_collapsible_career_table(self, table: Tag) -> Dict[str, Any] | None:
        """Parse collapsible career statistics table (e.g., motorcycle racing).
        
        Example structure:
        <table class="mw-collapsible">
          <tr><th>Title</th></tr>
          <tr><th>Active years</th><td>1960-1964</td></tr>
          <tr><th>Starts</th><td>129</td></tr>
          ...
        </table>
        """
        if not table:
            return None
        
        # Extract the title from the first row
        title_row = table.find("tr")
        title = None
        if title_row:
            title_th = title_row.find("th")
            if title_th:
                title = clean_infobox_text(title_th.get_text(" ", strip=True))
        
        # Parse all label-value rows
        rows = []
        for tr in table.find_all("tr"):
            # Skip the title row
            th_cells = tr.find_all("th")
            td_cells = tr.find_all("td")
            
            # If we have one th and one td, it's a label-value pair
            if len(th_cells) == 1 and len(td_cells) == 1:
                label = clean_infobox_text(th_cells[0].get_text(" ", strip=True))
                value_cell = td_cells[0]
                
                # Parse value based on label
                if label in {"Active years", "Years active"}:
                    value = self.parse_active_years(value_cell)
                elif label == "Team":
                    value = self.parse_teams(value_cell)
                elif label in {"Starts", "Wins", "Podiums", "Points"}:
                    value = self.parse_int_cell(value_cell)
                elif label in {"First race", "Last race", "First win", "Last win"}:
                    value = self.parse_race_event(value_cell)
                else:
                    value = self.parse_cell(value_cell)
                
                rows.append({
                    "label": label,
                    "value": value
                })
            # If we have a full-width row with colspan=2, it might be a stats table
            elif len(td_cells) == 1 and td_cells[0].get("colspan") == "2":
                nested_table = td_cells[0].find("table")
                if nested_table:
                    table_data = self.parse_nested_table(nested_table)
                    rows.append({"table": table_data})
        
        return {
            "title": title,
            "rows": rows
        } if rows else None
