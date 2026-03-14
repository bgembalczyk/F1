"""Engine-specific parsing helpers.

This module contains helper functions for parsing engine-related data
from Wikipedia tables.
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
from scrapers.base.table.columns.helpers.constants import AFTER_DISPLACEMENT_TYPE_RE
from scrapers.base.table.columns.helpers.constants import CC_TO_L_THRESHOLD
from scrapers.base.table.columns.helpers.constants import DISPLACEMENT_RE
from scrapers.base.table.columns.helpers.constants import EXACT_TYPE_RE
from scrapers.base.table.columns.helpers.constants import FUEL_TYPE_URLS
from scrapers.base.table.columns.helpers.constants import MODIFIER_ONLY_URLS
from scrapers.base.table.columns.helpers.constants import PLAIN_TEXT_TYPE_RE
from scrapers.base.table.columns.helpers.constants import TYPE_WITH_MODIFIER_RE
from scrapers.base.table.columns.helpers.constants import VERBOSE_TYPE_MAP
from scrapers.base.table.columns.helpers.hex_expanding import expand_hex_shorthand


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
            link_lookup: Pre-built lookup of engine names to links
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

        modifier_only = EngineParsingHelpers._try_modifier_only_segment(links)
        if modifier_only is not None:
            return modifier_only

        first_link = links[0] if links else None
        first_link_text = (first_link.get("text") or "") if first_link else ""

        special_tokens: set[str] = set()
        type_str, first_link, first_link_text = (
            EngineParsingHelpers._resolve_first_link_type(
                first_link,
                first_link_text,
                special_tokens,
            )
        )

        type_str, supercharged, turbocharged, gas_turbine, fuel_type = (
            EngineParsingHelpers._process_secondary_links(
                links[1:],
                type_str,
                special_tokens,
            )
        )

        displacement_l = EngineParsingHelpers.extract_displacement(text)

        type_str, turbocharged, supercharged = (
            EngineParsingHelpers._fallback_type_from_text(
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

        layout, cylinders = EngineParsingHelpers.parse_layout_and_cylinders(type_str)

        model_text = EngineParsingHelpers.extract_model_text(
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

    # ------------------------------------------------------------------
    # private helpers for parse_segment
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_modifier_flags(
        links: list[LinkRecord],
    ) -> tuple[str | None, bool, bool, bool]:
        """Extract fuel/induction modifier flags from links."""
        fuel_type: str | None = None
        supercharged = False
        turbocharged = False
        gas_turbine = False

        for link in links:
            url = (link.get("url") or "").lower()
            for url_key, ftype in FUEL_TYPE_URLS.items():
                if url_key in url:
                    fuel_type = ftype
            supercharged = (
                supercharged or "supercharger" in url or "supercharged" in url
            )
            turbocharged = (
                turbocharged or "turbocharger" in url or "turbocharging" in url
            )
            gas_turbine = gas_turbine or "gas_turbine" in url

        return fuel_type, supercharged, turbocharged, gas_turbine

    @staticmethod
    def _try_modifier_only_segment(
        links: list[LinkRecord],
    ) -> dict[str, object] | None:
        """Return a modifier-only dict when all links point to modifier URLs, else None.

        A segment whose every link resolves to a known modifier URL (diesel,
        supercharger, turbocharger, gas turbine) carries no engine model; it
        should be merged into the preceding engine entry.
        """
        if not links:
            return None
        all_link_urls = [(link.get("url") or "").lower() for link in links]
        if not all(
                any(mod in url for mod in MODIFIER_ONLY_URLS) for url in all_link_urls
        ):
            return None

        fuel_type, supercharged, turbocharged, gas_turbine = (
            EngineParsingHelpers._extract_modifier_flags(links)
        )

        result: dict[str, object] = {}
        if fuel_type is not None:
            result["fuel_type"] = fuel_type
        if supercharged:
            result["supercharged"] = True
        if turbocharged:
            result["turbocharged"] = True
        if gas_turbine:
            result["gas_turbine"] = True
        return result

    @staticmethod
    def _resolve_first_link_type(
        first_link: LinkRecord | None,
        first_link_text: str,
        special_tokens: set[str],
    ) -> tuple[str | None, LinkRecord | None, str]:
        """Determine the engine type from the first link, if it encodes one.

        Returns ``(type_str, first_link, first_link_text)`` — the latter two
        are set to ``(None, "")`` when the first link *is* the type token so
        that it is not used as the model URL.
        """
        if first_link_text and EXACT_TYPE_RE.match(first_link_text):
            special_tokens.add(first_link_text)
            return first_link_text, None, ""

        type_str: str | None = None
        if first_link_text:
            m = AFTER_DISPLACEMENT_TYPE_RE.search(first_link_text)
            if m:
                type_str = m.group(1)
        return type_str, first_link, first_link_text

    @staticmethod
    def _update_type_from_link_text(
        link_text: str,
        type_str: str | None,
        special_tokens: set[str],
    ) -> str | None:
        """Update type string from link text if no type has been resolved yet."""
        if type_str is not None:
            return type_str

        extracted_type = EngineParsingHelpers._extract_type_from_link(
            link_text,
            special_tokens,
        )
        if extracted_type is not None:
            return extracted_type

        m_type = AFTER_DISPLACEMENT_TYPE_RE.search(link_text)
        if m_type:
            return m_type.group(1)
        return None

    @staticmethod
    def _strip_type_modifier(
        type_str: str | None,
        *,
        supercharged: bool,
        turbocharged: bool,
    ) -> tuple[str | None, bool, bool]:
        """Strip trailing type modifiers (e.g. L4t -> L4) and set flags."""
        if type_str is None:
            return None, supercharged, turbocharged

        m_mod = TYPE_WITH_MODIFIER_RE.match(type_str)
        if not m_mod:
            return type_str, supercharged, turbocharged

        modifier = m_mod.group(2).lower()
        if modifier == "t":
            turbocharged = True
        elif modifier == "s":
            supercharged = True
        return m_mod.group(1), supercharged, turbocharged

    @staticmethod
    def _update_modifiers_from_url(
        url: str,
        link_text: str,
        special_tokens: set[str],
        *,
        supercharged: bool,
        turbocharged: bool,
        gas_turbine: bool,
        fuel_type: str | None,
    ) -> tuple[bool, bool, bool, str | None]:
        """Update modifier flags based on URL fragments."""
        if "supercharger" in url:
            supercharged = True
            special_tokens.add(link_text)
        if "turbocharger" in url or "turbo" in url:
            turbocharged = True
            special_tokens.add(link_text)
        if "gas_turbine" in url:
            gas_turbine = True
            special_tokens.add(link_text)
        if fuel_type is None:
            for url_key, ftype in FUEL_TYPE_URLS.items():
                if url_key in url:
                    fuel_type = ftype
                    special_tokens.add(link_text)
                    break
        return supercharged, turbocharged, gas_turbine, fuel_type

    @staticmethod
    def _process_secondary_links(
        links: list[LinkRecord],
        type_str: str | None,
        special_tokens: set[str],
    ) -> tuple[str | None, bool, bool, bool, str | None]:
        """Extract engine type and modifier flags from non-first links.

        Returns ``(type_str, supercharged, turbocharged, gas_turbine, fuel_type)``.
        """
        supercharged = False
        turbocharged = False
        gas_turbine = False
        fuel_type: str | None = None

        for link in links:
            link_text = link.get("text") or ""
            url = (link.get("url") or "").lower()

            type_str = EngineParsingHelpers._update_type_from_link_text(
                link_text,
                type_str,
                special_tokens,
            )
            type_str, supercharged, turbocharged = (
                EngineParsingHelpers._strip_type_modifier(
                    type_str,
                    supercharged=supercharged,
                    turbocharged=turbocharged,
                )
            )
            supercharged, turbocharged, gas_turbine, fuel_type = (
                EngineParsingHelpers._update_modifiers_from_url(
                    url,
                    link_text,
                    special_tokens,
                    supercharged=supercharged,
                    turbocharged=turbocharged,
                    gas_turbine=gas_turbine,
                    fuel_type=fuel_type,
                )
            )

        return type_str, supercharged, turbocharged, gas_turbine, fuel_type

    @staticmethod
    def _extract_type_from_link(
        link_text: str,
        special_tokens: set[str],
    ) -> str | None:
        """Return the engine type code represented by *link_text*, or ``None``.

        Handles exact codes (e.g. ``"V8"``), codes with a modifier suffix
        (e.g. ``"L4t"``), and verbose names (e.g. ``"Straight-4"``).
        Side-effects: adds *link_text* to *special_tokens* when a type is found.
        """
        if EXACT_TYPE_RE.match(link_text):
            special_tokens.add(link_text)
            return link_text

        m_mod = TYPE_WITH_MODIFIER_RE.match(link_text)
        if m_mod:
            special_tokens.add(link_text)
            return link_text  # modifier stripping happens in caller

        verbose_key = link_text.lower()
        if verbose_key in VERBOSE_TYPE_MAP:
            special_tokens.add(link_text)
            return VERBOSE_TYPE_MAP[verbose_key]

        return None

    @staticmethod
    def _fallback_type_from_text(
        text: str,
        type_str: str | None,
        *,
        turbocharged: bool,
        supercharged: bool,
    ) -> tuple[str | None, bool, bool]:
        """Scan plain segment text for a type code when no link provided one.

        Returns ``(type_str, turbocharged, supercharged)``.
        """
        if type_str is not None:
            return type_str, turbocharged, supercharged

        m_plain = PLAIN_TEXT_TYPE_RE.search(text)
        if not m_plain:
            return None, turbocharged, supercharged

        candidate = m_plain.group(1)
        m_mod = TYPE_WITH_MODIFIER_RE.match(candidate)
        if m_mod:
            modifier = m_mod.group(2).lower()
            if modifier == "t":
                turbocharged = True
            elif modifier == "s":
                supercharged = True
            return m_mod.group(1), turbocharged, supercharged

        return candidate, turbocharged, supercharged

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
        # First try: number followed by litre unit or start of type indicator
        # (e.g. "1.5 L8").
        match = re.search(r"(\d+\.?\d*)\s*(?:L|l|litre|litres|cc|cm³)", text)
        if match:
            value = parse_float_from_text(match.group(1))
            if "cc" in text.lower() or "cm" in text.lower():
                if value and value > CC_TO_L_THRESHOLD:
                    value = value / 1000
            return value
        # Fallback: bare decimal number (e.g. "3.0 V8")
        match = re.search(r"\b(\d+\.\d+)\b", text)
        if match:
            return parse_float_from_text(match.group(1))
        return None

    @staticmethod
    def _trim_text_before_displacement(text: str) -> str:
        """Return text prefix that appears before displacement tokens."""
        disp_match = DISPLACEMENT_RE.search(text)
        if not disp_match:
            return text
        return text[: disp_match.start()].strip() or text

    @staticmethod
    def _strip_special_suffix_tokens(
        suffix: str,
        special_tokens: set[str] | None,
    ) -> str:
        """Strip suffix words after the first special token."""
        if not (special_tokens and suffix):
            return suffix

        lower_tokens = {token.lower() for token in special_tokens}
        clean_words: list[str] = []
        for word in suffix.split():
            if word.lower() in lower_tokens:
                break
            clean_words.append(word)
        return " ".join(clean_words).strip()

    @staticmethod
    def _extract_model_suffix(
        after_link: str,
        special_tokens: set[str] | None,
    ) -> str:
        """Extract model suffix from text following first link text."""
        disp_match = DISPLACEMENT_RE.search(after_link)
        if disp_match:
            return after_link[: disp_match.start()].strip()

        raw_suffix = after_link.strip()
        return EngineParsingHelpers._strip_special_suffix_tokens(
            raw_suffix,
            special_tokens,
        )

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
        - text="Alfa Romeo 158 1.5 L8 s", first_link_text="Alfa Romeo"
          -> "Alfa Romeo 158"
        - text="Ford Cosworth DFV 3.0 V8", first_link_text="Ford Cosworth DFV"
          -> "Ford Cosworth DFV"
        - text="Climax FPF 2.0 L4", first_link_text="Climax FPF 2.0 L4"
          -> "Climax FPF"

        Args:
            text: Full cleaned text of the engine segment
            first_link_text: Text of the first (manufacturer) link
            displacement_l: Extracted displacement value
                (used to locate suffix boundary)
            special_tokens: Link texts with special meaning
                (type codes, "s", "tbn", etc.)
                that should not appear in the model name suffix.

        Returns:
            Combined model text string
        """
        if not first_link_text:
            if displacement_l is None or not text:
                return text
            return EngineParsingHelpers._trim_text_before_displacement(text)

        pos = text.find(first_link_text)
        if pos < 0:
            return first_link_text

        after_link = text[pos + len(first_link_text) :]
        if not after_link.strip():
            return EngineParsingHelpers._trim_text_before_displacement(first_link_text)

        model_suffix = EngineParsingHelpers._extract_model_suffix(
            after_link,
            special_tokens,
        )
        if not model_suffix:
            return first_link_text
        return f"{first_link_text} {model_suffix}"

    @staticmethod
    def parse_layout_and_cylinders(
        type_str: str | None,
    ) -> tuple[str | None, int | None]:
        """
        Parse engine layout letter and cylinder count from a type string
        like "V8" or "L6".

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
