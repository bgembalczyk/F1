"""Helper class for parsing nationality from infobox cells."""

import re
from typing import Any
from typing import Dict
from typing import List

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.helpers.text_normalization import clean_infobox_text


class NationalityParser:
    """Handles parsing of nationality information with optional year ranges."""

    @staticmethod
    def parse_nationality(cell: Tag) -> List[str] | List[Dict[str, Any]]:
        """Parse nationality field.

        Handles cases like:
        - "American or Italian" -> ["American", "Italian"]
        - "Federation of Rhodesia and Nyasaland (1963)" with year ranges -> structured data
        
        Args:
            cell: BeautifulSoup Tag representing the cell
            
        Returns:
            List of nationality strings or list of dictionaries with nationality and years
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
