"""Engine-specific parsing helpers.

This module contains helper functions for parsing engine-related data from Wikipedia tables.
Extracted from scrapers/base/table/columns/helpers.py to follow SRP.

Follows SOLID principles:
- Single Responsibility: Handles only engine-related parsing
- High Cohesion: All functions work together for engine parsing
- Information Expert: Engine parsing logic grouped with engine data
"""
import re
from typing import Optional

from bs4 import Tag

from models.records.link import LinkRecord
from scrapers.base.helpers.background import extract_background
from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.parsing import parse_float_from_text
from scrapers.base.helpers.text import clean_wiki_text


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
        return bg_lower in {"#efefef", "#f0f0f0", "#e0e0e0", "lightgrey", "lightgray"}

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
            Dictionary with engine data including name, specifications, etc.
        """
        links = normalize_links(segment.find_all("a", href=True), base_url)
        text = clean_wiki_text(segment.get_text(" ", strip=True))

        engine_link = None
        if links:
            engine_text = links[0].get("text", "")
            if engine_text:
                key = engine_text.strip().lower()
                matched = link_lookup.get(key, [links[0]])
                if matched:
                    engine_link = matched[0]

        displacement = EngineParsingHelpers.extract_displacement(text)
        type_text = EngineParsingHelpers.extract_type_text(text, displacement)
        engine_type, cylinders = EngineParsingHelpers.parse_engine_type(type_text)

        return {
            "engine": engine_link,
            "displacement": displacement,
            "type": engine_type,
            "cylinders": cylinders,
            "supercharged": EngineParsingHelpers.extract_supercharged(text),
            "turbocharged": EngineParsingHelpers.extract_turbocharged(text),
            "gas_turbine": EngineParsingHelpers.extract_gas_turbine(text),
        }

    @staticmethod
    def extract_displacement(text: str) -> float | None:
        """
        Extract engine displacement in litres from text (e.g., "3.0L" -> 3.0).
        
        Args:
            text: Text potentially containing displacement information
            
        Returns:
            Displacement in litres, or None if not found
        """
        if not text:
            return None
        # Look for patterns like "3.0L", "1.5 L", "3000cc"
        match = re.search(r"(\d+\.?\d*)\s*(?:L|l|litre|litres|cc|cm³)", text)
        if match:
            value = parse_float_from_text(match.group(1))
            # Convert cc to litres if needed
            if "cc" in text.lower() or "cm" in text.lower():
                if value and value > 100:  # Likely in cc
                    value = value / 1000
            return value
        return None

    @staticmethod
    def extract_type_text(text: str, displacement: float | None) -> str | None:
        """
        Extract engine type description text, excluding displacement.
        
        Args:
            text: Full engine description text
            displacement: Extracted displacement value (to remove from type)
            
        Returns:
            Engine type text, or None
        """
        if not text:
            return None
        
        # Remove displacement notation
        cleaned = re.sub(r"\d+\.?\d*\s*(?:L|l|litre|litres|cc|cm³)", "", text)
        cleaned = cleaned.strip(" -–—()")
        
        if not cleaned:
            return None
        
        return cleaned

    @staticmethod
    def parse_engine_type(type_text: str | None) -> tuple[str | None, int | None]:
        """
        Parse engine type and cylinder count from type text.
        
        Args:
            type_text: Engine type description (e.g., "V8", "Inline-4")
            
        Returns:
            Tuple of (engine_type, cylinder_count)
        """
        if not type_text:
            return None, None
        
        # Look for patterns like V8, I4, Inline-6, Straight-4, etc.
        match = re.search(r"([VI]|Inline|Straight|Flat)[-\s]*(\d+)", type_text, re.IGNORECASE)
        if match:
            config = match.group(1).upper()
            if config in {"INLINE", "STRAIGHT"}:
                config = "I"
            cylinders = int(match.group(2))
            return f"{config}{cylinders}", cylinders
        
        return type_text, None

    @staticmethod
    def extract_supercharged(text: str) -> bool | None:
        """Check if engine is supercharged."""
        if not text:
            return None
        text_lower = text.lower()
        if "supercharged" in text_lower or "supercharger" in text_lower:
            return True
        return None

    @staticmethod
    def extract_turbocharged(text: str) -> bool | None:
        """Check if engine is turbocharged."""
        if not text:
            return None
        text_lower = text.lower()
        if "turbo" in text_lower:
            return True
        return None

    @staticmethod
    def extract_gas_turbine(text: str) -> bool | None:
        """Check if engine is a gas turbine."""
        if not text:
            return None
        text_lower = text.lower()
        if "gas turbine" in text_lower or "jet engine" in text_lower:
            return True
        return None


# Backward compatibility functions
def build_engine_link_lookup(links: list[LinkRecord]) -> dict[str, list[LinkRecord]]:
    """Build engine link lookup. Deprecated: Use EngineParsingHelpers.build_link_lookup()"""
    return EngineParsingHelpers.build_link_lookup(links)


def extract_engine_class(cell: Tag) -> str | None:
    """Extract engine class. Deprecated: Use EngineParsingHelpers.extract_engine_class()"""
    return EngineParsingHelpers.extract_engine_class(cell)


def is_f2_background(background: str) -> bool:
    """Check F2 background. Deprecated: Use EngineParsingHelpers.is_f2_background()"""
    return EngineParsingHelpers.is_f2_background(background)


def parse_engine_segment(
    segment: Tag,
    link_lookup: dict[str, list[LinkRecord]],
    base_url: str,
) -> dict[str, object]:
    """Parse engine segment. Deprecated: Use EngineParsingHelpers.parse_segment()"""
    return EngineParsingHelpers.parse_segment(segment, link_lookup, base_url)


def extract_displacement(text: str) -> float | None:
    """Extract displacement. Deprecated: Use EngineParsingHelpers.extract_displacement()"""
    return EngineParsingHelpers.extract_displacement(text)


def extract_type_text(text: str, displacement: float | None) -> str | None:
    """Extract type text. Deprecated: Use EngineParsingHelpers.extract_type_text()"""
    return EngineParsingHelpers.extract_type_text(text, displacement)


def parse_engine_type(type_text: str | None) -> tuple[str | None, int | None]:
    """Parse engine type. Deprecated: Use EngineParsingHelpers.parse_engine_type()"""
    return EngineParsingHelpers.parse_engine_type(type_text)


def extract_supercharged(text: str) -> bool | None:
    """Extract supercharged. Deprecated: Use EngineParsingHelpers.extract_supercharged()"""
    return EngineParsingHelpers.extract_supercharged(text)


def extract_turbocharged(text: str) -> bool | None:
    """Extract turbocharged. Deprecated: Use EngineParsingHelpers.extract_turbocharged()"""
    return EngineParsingHelpers.extract_turbocharged(text)


def extract_gas_turbine(text: str) -> bool | None:
    """Extract gas turbine. Deprecated: Use EngineParsingHelpers.extract_gas_turbine()"""
    return EngineParsingHelpers.extract_gas_turbine(text)
