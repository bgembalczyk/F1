import re
from typing import Any
from typing import Dict
from typing import List

from bs4 import BeautifulSoup
from bs4 import Tag

from models.records.link import LinkRecord
from models.services.helpers import parse_int_values
from models.services.helpers import split_delimited_text
from scrapers.base.errors import DomainParseError
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.drivers.infobox.parsers.best_finish_parser import BestFinishParser
from scrapers.drivers.infobox.parsers.licence_parser import LicenceParser
from scrapers.drivers.infobox.parsers.link_extractor import InfoboxLinkExtractor
from scrapers.drivers.infobox.parsers.season_parser import SeasonParser
from scrapers.drivers.infobox.parsers.year_parser import YearParser


class InfoboxCellParser:
    """Parser for individual infobox cells.
    
    This class delegates complex parsing tasks to specialized helper classes:
    - YearParser: for year and year range parsing
    - SeasonParser: for season validation and class detection
    - LicenceParser: for racing licence parsing
    - BestFinishParser: for best finish result parsing
    """

    def __init__(
        self, *, include_urls: bool, link_extractor: InfoboxLinkExtractor
    ) -> None:
        self._include_urls = include_urls
        self._link_extractor = link_extractor
        
        # Initialize helper parsers (for classes that need state)
        self._season_parser = SeasonParser()
        self._licence_parser = LicenceParser(link_extractor)
        self._best_finish_parser = BestFinishParser(link_extractor)

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
            year_match = re.search(r"\b(\d{4})\b", link_text)
            if year_match:
                year = int(year_match.group(1))
                year_to_link[year] = link.get("url")

        # Extract all years and ranges from text
        years_set: set[int] = set()

        # Find ranges like "2007-2008" or "2007–2008"
        for match in re.finditer(r"\b(\d{4})\s*[-–]\s*(\d{2,4})\b", text):
            start = int(match.group(1))
            end_text = match.group(2)
            if len(end_text) == 2:
                end = (start // 100) * 100 + int(end_text)
            else:
                end = int(end_text)
            for year in range(start, end + 1):
                years_set.add(year)

        # Find individual years
        for match in re.finditer(r"\b(\d{4})\b", text):
            year = int(match.group(1))
            years_set.add(year)

        # Try to interpolate URLs for missing years
        if len(year_to_link) >= 2:
            # Detect URL pattern
            url_pattern = YearParser.detect_url_pattern(year_to_link)
            if url_pattern:
                for year in years_set:
                    if year not in year_to_link:
                        year_to_link[year] = url_pattern.replace("{year}", str(year))

        # Build result list
        result = []
        for year in sorted(years_set):
            result.append({"year": year, "url": year_to_link.get(year)})

        return result

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

            return {"count": count, "championships": championships}
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
                year_match = re.search(r"\b(\d{4})\b", link_text)
                if year_match:
                    year = int(year_match.group(1))
                    year_to_url[year] = link.get("url")

            # Extract all years from text (typically in parentheses or <small> tag)
            # Check <small> tag first
            small_tag = cell.find("small")
            if small_tag:
                small_text = (
                    clean_infobox_text(small_tag.get_text(" ", strip=True)) or ""
                )
                for year_match in re.finditer(r"\b(\d{4})\b", small_text):
                    year = int(year_match.group(1))
                    wins.append({"year": year, "url": year_to_url.get(year)})
            else:
                # Fallback to extracting from parentheses in main text
                paren_match = re.search(r"\(([^)]+)\)", text)
                if paren_match:
                    paren_content = paren_match.group(1)
                    for year_match in re.finditer(r"\b(\d{4})\b", paren_content):
                        year = int(year_match.group(1))
                        wins.append({"year": year, "url": year_to_url.get(year)})

            return {"count": count, "wins": wins}
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
                YearParser.parse_year_range(years_text)
                if years_text
                else {"start": None, "end": None}
            )
            entries.append({"number": number, "years": years})
        return entries

    def parse_best_finish(self, cell: Tag) -> Dict[str, Any]:
        """Parse best finish field - delegates to BestFinishParser."""
        return self._best_finish_parser.parse_best_finish(cell)

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

    def parse_finished_last_season(self, cell: Tag) -> Dict[str, Any]:
        """Parse 'Finished last season' field.

        Example: "14th (62 pts)" -> {position: "14th", points: 62}
        """
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        try:
            result: Dict[str, Any] = {"position": None, "points": None}

            # Extract position (before parentheses)
            pos_match = re.match(r"^([^(]+)", text)
            if pos_match:
                result["position"] = pos_match.group(1).strip() or None

            # Extract points from parentheses
            pts_match = re.search(r"\((\d+(?:\.\d+)?)\s*pts?\)", text)
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
        """Parse 'Racing licence' field - delegates to LicenceParser."""
        return self._licence_parser.parse_racing_licence(cell)

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
            races_run_match = re.match(r"^(\d+)\s+races?\s+run\s+over", text)
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
        return (
            normalized == expected_wins_podiums_poles
            or normalized == expected_wins_topten_poles
        )

    @staticmethod
    def _extract_stats_from_table(table_data: Dict[str, Any]) -> Dict[str, int | None]:
        """Extract Wins, Podiums/Top tens, Poles from stats table."""
        headers = table_data.get("headers", [])
        normalized = [h.lower().strip() for h in headers]

        stats: Dict[str, int | None] = {
            "wins": None,
            "podiums": None,
            "top_tens": None,
            "poles": None,
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
        has_years = re.search(r"\(\s*\d{4}", text)

        if has_years:
            # Parse structured nationality with years
            # Split by <br> tags to separate different nationalities
            html = str(cell)
            parts = re.split(r"<br\s*/?>", html, flags=re.IGNORECASE)

            nationalities = []

            for part_html in parts:
                if not part_html.strip():
                    continue

                # Parse this part
                part_soup = BeautifulSoup(part_html, "html.parser")
                part_text = (
                    clean_infobox_text(part_soup.get_text(" ", strip=True)) or ""
                )

                # Extract nationality name (before any year information)
                # Pattern: "Nationality_name (year)" or "Nationality_name (year, year-year)"
                # Remove year information to get nationality name
                nationality_name = re.sub(
                    r"\s*\([^)]*\d{4}[^)]*\)", "", part_text
                ).strip()

                # Extract all year patterns from this part
                # Look for individual years and year ranges in <small> tags or parentheses
                years = []

                # Find all year patterns in text
                # Pattern 1: (1963) -> single year
                # Pattern 2: (1965, 1967-1968) -> multiple years and ranges
                year_patterns = re.findall(r"\(([^)]*\d{4}[^)]*)\)", part_text)

                for year_pattern in year_patterns:
                    # Extract individual years and ranges
                    # Find ranges first
                    for range_match in re.finditer(
                        r"(\d{4})\s*[-–]\s*(\d{4})", year_pattern
                    ):
                        start = int(range_match.group(1))
                        end = int(range_match.group(2))
                        for year in range(start, end + 1):
                            if year not in years:
                                years.append(year)

                    # Find individual years
                    for year_match in re.finditer(r"\b(\d{4})\b", year_pattern):
                        year = int(year_match.group(1))
                        if year not in years:
                            years.append(year)

                if nationality_name and years:
                    nationalities.append(
                        {"nationality": nationality_name, "years": sorted(years)}
                    )
                elif nationality_name:
                    # Nationality without specific years
                    nationalities.append({"nationality": nationality_name, "years": []})

            return nationalities if nationalities else []
        else:
            # Simple case: just extract nationality names separated by "or"
            # Split by "or" to get multiple nationalities
            parts = re.split(r"\s+or\s+", text, flags=re.IGNORECASE)
            nationalities = []

            for part in parts:
                # Clean up each part
                part = part.strip()
                # Remove any reference markers like [1]
                part = re.sub(r"\[\d+\]", "", part).strip()
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

                rows.append({"label": label, "value": value})
            # If we have a full-width row with colspan=2, it might be a stats table
            elif len(td_cells) == 1 and td_cells[0].get("colspan") == "2":
                nested_table = td_cells[0].find("table")
                if nested_table:
                    table_data = self.parse_nested_table(nested_table)
                    rows.append({"table": table_data})

        return {"title": title, "rows": rows} if rows else None
