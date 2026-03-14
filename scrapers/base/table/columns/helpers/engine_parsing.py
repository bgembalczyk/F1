"""Engine-specific parsing helpers.

This module contains the top-level orchestration for parsing engine-related
data from Wikipedia table cells.  Low-level helpers have been extracted into
dedicated modules following SRP:

- ``engine_link_helpers``  — resolving type codes and modifier flags from links
- ``engine_text_helpers``  — extracting displacement, model text and layout
  from plain text

Follows SOLID principles:
- Single Responsibility: Orchestrates engine segment parsing only
- Open/Closed: Extensible via the two helper classes without modification
- Dependency Inversion: Depends on abstractions (helper classes), not details
"""

import re

from bs4 import Tag

from models.records.link import LinkRecord
from scrapers.base.helpers.background import extract_background
from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.helpers.url import normalize_url
from scrapers.base.table.columns.helpers.engine_link_helpers import EngineLinkHelpers
from scrapers.base.table.columns.helpers.engine_text_helpers import EngineTextHelpers
from scrapers.base.table.columns.helpers.hex_expanding import expand_hex_shorthand


class EngineParsingHelpers:
    """
    Orchestration class for parsing engine information from table cells.

    Provides the public API for:
    - Building engine link lookups (delegates to EngineLinkHelpers)
    - Parsing engine segments into structured data
    - Extracting engine class from cell background colour

    Low-level link and text parsing is handled by EngineLinkHelpers and
    EngineTextHelpers respectively.
    """

    @staticmethod
    def build_link_lookup(links: list[LinkRecord]) -> dict[str, list[LinkRecord]]:
        """
        Build lookup dictionary mapping engine names to their link records.

        Delegates to :meth:`EngineLinkHelpers.build_link_lookup`.
        """
        return EngineLinkHelpers.build_link_lookup(links)

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
        bg_lower = expand_hex_shorthand(bg_lower)
        # Common F2 background colors in Wikipedia tables
        return bg_lower in {
            "#efefef",
            "#f0f0f0",
            "#e0e0e0",
            "#ffcccc",
            "lightgrey",
            "lightgray",
        }

    @staticmethod
    def parse_segment(
        segment: Tag,
        _link_lookup: dict[str, list[LinkRecord]],
        base_url: str,
    ) -> dict[str, object]:
        """
        Parse an engine segment into structured data.

        Args:
            segment: HTML tag containing engine information
            _link_lookup: Pre-built lookup of engine names to links (unused,
                kept for API compatibility)
            base_url: Base URL for resolving relative links

        Returns:
            Dictionary with engine data including model, displacement_l, type,
            layout, cylinders and optional supercharged/turbocharged/gas_turbine flags.
        """
        links = normalize_links(
            segment,
            full_url=lambda href: normalize_url(base_url, href),
        )
        text = clean_wiki_text(segment.get_text(" ", strip=True))

        modifier_only = EngineLinkHelpers.try_modifier_only_segment(links)
        if modifier_only is not None:
            return modifier_only

        first_link = links[0] if links else None
        first_link_text = (first_link.get("text") or "") if first_link else ""

        special_tokens: set[str] = set()
        type_str, first_link, first_link_text = (
            EngineLinkHelpers.resolve_first_link_type(
                first_link,
                first_link_text,
                special_tokens,
            )
        )

        type_str, supercharged, turbocharged, gas_turbine, fuel_type = (
            EngineLinkHelpers.process_secondary_links(
                links[1:],
                type_str,
                special_tokens,
            )
        )

        displacement_l = EngineTextHelpers.extract_displacement(text)

        type_str, turbocharged, supercharged = (
            EngineTextHelpers.fallback_type_from_text(
                text,
                type_str,
                turbocharged=turbocharged,
                supercharged=supercharged,
            )
        )

        if not turbocharged and re.search(r"\bturbo\b", text, re.IGNORECASE):
            turbocharged = True
        if fuel_type is None and re.search(r"\bdiesel\b", text, re.IGNORECASE):
            fuel_type = "diesel"

        layout, cylinders = EngineTextHelpers.parse_layout_and_cylinders(type_str)

        model_text = EngineTextHelpers.extract_model_text(
            text,
            first_link_text,
            displacement_l,
            special_tokens,
        )
        model: dict[str, object] | None = None
        if model_text or first_link:
            model = {
                "text": model_text,
                "url": first_link.get("url") if first_link else None,
            }

        return EngineParsingHelpers._build_engine_result(
            model,
            displacement_l,
            type_str,
            layout,
            cylinders,
            supercharged=supercharged,
            turbocharged=turbocharged,
            gas_turbine=gas_turbine,
            fuel_type=fuel_type,
        )

    @staticmethod
    def _build_engine_result(
        model: dict[str, object] | None,
        displacement_l: float | None,
        type_str: str | None,
        layout: str | None,
        cylinders: int | None,
        *,
        supercharged: bool,
        turbocharged: bool,
        gas_turbine: bool,
        fuel_type: str | None,
    ) -> dict[str, object]:
        """Assemble the final engine result dict, omitting absent/False fields."""
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
        if fuel_type is not None:
            result["fuel_type"] = fuel_type
        return result
