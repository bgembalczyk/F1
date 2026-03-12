"""Engine-specific parsing helpers.

This module contains helper functions for parsing engine-related data from Wikipedia tables.
Extracted from scrapers/base/table/columns/helpers.py to follow SRP.

Follows SOLID principles:
- Single Responsibility: Handles only engine-related parsing
- High Cohesion: All functions work together for engine parsing
- Information Expert: Engine parsing logic grouped with engine data
"""
import re

from bs4 import Tag

from models.records.link import LinkRecord
from scrapers.base.helpers.background import extract_background
from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.parsing import parse_float_from_text
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.helpers.url import normalize_url

# Pattern that matches a displacement value followed by an explicit unit (e.g. "1.5 L",
# "1.5 L8" where L starts the type, "3000cc") or a bare decimal (e.g. "3.0 V8").
_DISPLACEMENT_RE = re.compile(
    r"\b\d+\.?\d*\s*(?:L|l|litre|litres|cc|cm³)|\b\d+\.\d+\b"
)

# Exact engine type code (e.g. "V8", "L4", "F4").
_EXACT_TYPE_RE = re.compile(r"^[A-Za-z]\d+$")

# Engine type embedded at end of text after a displacement number
# (e.g. "Climax FPF 2.0 L4" → "L4", "620 3.0 V8" → "V8").
_AFTER_DISPLACEMENT_TYPE_RE = re.compile(r"\b\d+\.?\d*\s+([A-Za-z]\d+)\s*$")


class EngineParsingHelpers:
    """
    Helper class for parsing engine information from table cells.
    
    Provides methods for:
    - Building engine link lookups
    - Parsing engine segments with specifications
    - Extracting engine properties (displacement, type, etc.)
    """

    @staticmethod
    def build_link_lookup(links: list[LinkRecord]) -> dict[str, list[LinkRecord]]:
        """
        Build lookup dictionary mapping engine names to their link records.
        
        Args:
            links: List of link records for engines
            
        Returns:
            Dictionary mapping lowercase engine names to lists of matching links
        """
        lookup: dict[str, list[LinkRecord]] = {}
        for link in links:
            text = link.get("text")
            if not text:
                continue
            key = text.strip().lower()
            if key not in lookup:
                lookup[key] = []
            lookup[key].append(link)
        return lookup

    @staticmethod
    def extract_engine_class(cell: Tag) -> str | None:
        """
        Extract engine class from cell background color (e.g., F2 engines).
        
        Args:
            cell: HTML table cell element
            
        Returns:
            Engine class identifier (e.g., "F2") or None
        """
        background = extract_background(cell)
        if EngineParsingHelpers.is_f2_background(background):
            return "F2"
        return None

    @staticmethod
    def is_f2_background(background: str) -> bool:
        """
        Check if background color indicates Formula 2 engine.
        
        Args:
            background: Background color string
            
        Returns:
            True if background indicates F2, False otherwise
        """
        if not background:
            return False
        bg_lower = background.lower().replace(" ", "")
        # Common F2 background colors in Wikipedia tables
        return bg_lower in {"#efefef", "#f0f0f0", "#e0e0e0", "#ffcccc", "lightgrey", "lightgray"}

    @staticmethod
    def parse_segment(
            segment: Tag,
            link_lookup: dict[str, list[LinkRecord]],
            base_url: str,
    ) -> dict[str, object]:
        """
        Parse an engine segment into structured data.

        Args:
            segment: HTML tag containing engine information
            link_lookup: Pre-built lookup of engine names to links
            base_url: Base URL for resolving relative links

        Returns:
            Dictionary with engine data including model, displacement_l, type,
            layout, cylinders and optional supercharged/turbocharged/gas_turbine flags.
        """
        links = normalize_links(segment, full_url=lambda href: normalize_url(base_url, href))
        text = clean_wiki_text(segment.get_text(" ", strip=True))

        first_link = links[0] if links else None
        first_link_text = (first_link.get("text") or "") if first_link else ""

        type_str: str | None = None
        supercharged = False
        turbocharged = False
        gas_turbine = False
        # Tokens from separate links that carry special meaning and must not
        # appear in the model-name suffix (e.g. engine type codes, "s", "tbn").
        special_tokens: set[str] = set()

        # Check if the first link is itself an engine type code (e.g. "L4").
        # In that case the plain text that precedes it is the model name.
        first_link_is_type = first_link_text and _EXACT_TYPE_RE.match(first_link_text)
        if first_link_is_type:
            type_str = first_link_text
            special_tokens.add(first_link_text)
            first_link = None
            first_link_text = ""
        else:
            # Engine type may be embedded inside the first link text after the
            # displacement value (e.g. "Climax FPF 2.0 L4" → "L4").
            if first_link_text:
                m = _AFTER_DISPLACEMENT_TYPE_RE.search(first_link_text)
                if m:
                    type_str = m.group(1)

        for link in links[1:]:
            link_text = link.get("text") or ""
            url = (link.get("url") or "").lower()

            if type_str is None:
                if _EXACT_TYPE_RE.match(link_text):
                    type_str = link_text
                    special_tokens.add(link_text)
                else:
                    m = _AFTER_DISPLACEMENT_TYPE_RE.search(link_text)
                    if m:
                        type_str = m.group(1)

            if "supercharger" in url:
                supercharged = True
                special_tokens.add(link_text)

            if "turbocharger" in url or "turbo" in url:
                turbocharged = True
                special_tokens.add(link_text)

            if "gas_turbine" in url:
                gas_turbine = True
                special_tokens.add(link_text)

        displacement_l = EngineParsingHelpers.extract_displacement(text)

        layout, cylinders = EngineParsingHelpers.parse_layout_and_cylinders(type_str)

        model_text = EngineParsingHelpers.extract_model_text(
            text, first_link_text, displacement_l, special_tokens
        )
        model: dict[str, object] | None = None
        if model_text or first_link:
            model = {
                "text": model_text,
                "url": first_link.get("url") if first_link else None,
            }

        result: dict[str, object] = {}
        if model is not None:
            result["model"] = model
        if displacement_l is not None:
            result["displacement_l"] = displacement_l
        if type_str is not None:
            result["type"] = type_str
        if layout is not None:
            result["layout"] = layout
        if cylinders is not None:
            result["cylinders"] = cylinders
        if supercharged:
            result["supercharged"] = True
        if turbocharged:
            result["turbocharged"] = True
        if gas_turbine:
            result["gas_turbine"] = True

        return result

    @staticmethod
    def extract_displacement(text: str) -> float | None:
        """
        Extract engine displacement in litres from text.

        Handles formats like "1.5 L8" (displacement before type link),
        "3.0 V8", "3.0 L V8" (explicit litre unit), "3000cc".

        Args:
            text: Text potentially containing displacement information

        Returns:
            Displacement in litres, or None if not found
        """
        if not text:
            return None
        # First try: number followed by litre unit or start of type indicator (e.g. "1.5 L8")
        match = re.search(r"(\d+\.?\d*)\s*(?:L|l|litre|litres|cc|cm³)", text)
        if match:
            value = parse_float_from_text(match.group(1))
            if "cc" in text.lower() or "cm" in text.lower():
                if value and value > 100:
                    value = value / 1000
            return value
        # Fallback: bare decimal number (e.g. "3.0 V8")
        match = re.search(r"\b(\d+\.\d+)\b", text)
        if match:
            return parse_float_from_text(match.group(1))
        return None
    @staticmethod
    def extract_model_text(
            text: str,
            first_link_text: str,
            displacement_l: float | None,
            special_tokens: set[str] | None = None,
    ) -> str:
        """
        Extract the full model text by combining the first link text with any
        model number/suffix that appears before the displacement value.

        For example:
        - text="Alfa Romeo 158 1.5 L8 s", first_link_text="Alfa Romeo" -> "Alfa Romeo 158"
        - text="Ford Cosworth DFV 3.0 V8", first_link_text="Ford Cosworth DFV" -> "Ford Cosworth DFV"
        - text="Climax FPF 2.0 L4", first_link_text="Climax FPF 2.0 L4" -> "Climax FPF"

        Args:
            text: Full cleaned text of the engine segment
            first_link_text: Text of the first (manufacturer) link
            displacement_l: Extracted displacement value (used to locate suffix boundary)
            special_tokens: Link texts with special meaning (type codes, "s", "tbn", etc.)
                that should not appear in the model name suffix.

        Returns:
            Combined model text string
        """
        if not first_link_text:
            if displacement_l is not None and text:
                match = _DISPLACEMENT_RE.search(text)
                if match:
                    return text[: match.start()].strip() or text
            return text

        pos = text.find(first_link_text)
        if pos < 0:
            return first_link_text

        after_link = text[pos + len(first_link_text):]
        if not after_link.strip():
            # The entire segment text is (or is contained within) the first link text.
            # Strip any trailing displacement and engine-type tokens that were included
            # in the link text (e.g. "Climax FPF 2.0 L4" → "Climax FPF").
            disp_match = _DISPLACEMENT_RE.search(first_link_text)
            if disp_match:
                return first_link_text[: disp_match.start()].strip() or first_link_text
            return first_link_text

        # Find where displacement begins in the text after the first link
        disp_match = _DISPLACEMENT_RE.search(after_link)
        if disp_match:
            model_suffix = after_link[: disp_match.start()].strip()
        else:
            model_suffix = after_link.strip()
            # Strip trailing tokens that belong to the engine specification
            # (e.g. "tbn" for gas turbine) rather than the model name.
            if special_tokens and model_suffix:
                lower_tokens = {t.lower() for t in special_tokens}
                words = model_suffix.split()
                clean_words = []
                for word in words:
                    if word.lower() in lower_tokens:
                        break
                    clean_words.append(word)
                model_suffix = " ".join(clean_words).strip()

        if model_suffix:
            return first_link_text + " " + model_suffix
        return first_link_text

    @staticmethod
    def parse_layout_and_cylinders(type_str: str | None) -> tuple[str | None, int | None]:
        """
        Parse engine layout letter and cylinder count from a type string like "V8" or "L6".

        Args:
            type_str: Engine type string (e.g., "V8", "L8", "F4")

        Returns:
            Tuple of (layout_letter, cylinder_count) or (None, None) if not parseable
        """
        if not type_str:
            return None, None
        match = re.match(r"^([A-Za-z])(\d+)$", type_str)
        if match:
            return match.group(1).upper(), int(match.group(2))
        return None, None
