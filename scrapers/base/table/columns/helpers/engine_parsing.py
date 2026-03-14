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
    r"\b\d+\.?\d*\s*(?:L|l|litre|litres|cc|cm³)|\b\d+\.\d+\b",
)

# Exact engine type code (e.g. "V8", "L4", "F4").
_EXACT_TYPE_RE = re.compile(r"^[A-Za-z]\d+$")

# Engine type code with a single-character modifier suffix:
#   't' suffix → turbocharged  (e.g. "L4t")
#   's' suffix → supercharged  (e.g. "L4s")
_TYPE_WITH_MODIFIER_RE = re.compile(r"^([A-Za-z]\d+)([ts])$", re.IGNORECASE)

# Engine type embedded at end of text after a displacement number
# (e.g. "Climax FPF 2.0 L4" → "L4", "620 3.0 V8" → "V8").
_AFTER_DISPLACEMENT_TYPE_RE = re.compile(r"\b\d+\.?\d*\s+([A-Za-z]\d+)\s*$")

# Engine type code appearing anywhere in plain text (e.g. "V12", "V8", "L4" after displacement).
# Restricted to known layout letters and 1–2 digit cylinder counts to avoid false positives.
_PLAIN_TEXT_TYPE_RE = re.compile(r"\b([VLFHR]\d{1,2}[ts]?)\b")

# Mapping from verbose/human-readable engine type names (as they appear in Wikipedia link text)
# to canonical type codes.
_VERBOSE_TYPE_MAP: dict[str, str] = {
    "straight-4": "L4",
    "inline-four": "L4",
    "inline-four engine": "L4",
    "straight-4 engine": "L4",
    "flat-4": "F4",
    "horizontally opposed 4": "F4",
    "straight-6": "L6",
    "inline-six": "L6",
    "inline-six engine": "L6",
    "straight-6 engine": "L6",
    "flat-6": "F6",
    "straight-8": "L8",
    "inline-eight": "L8",
    "straight-8 engine": "L8",
    "flat-8": "F8",
    "v6": "V6",
    "v6 engine": "V6",
    "v8": "V8",
    "v8 engine": "V8",
    "v10": "V10",
    "v10 engine": "V10",
    "v12": "V12",
    "v12 engine": "V12",
    "v16": "V16",
    "flat-12": "F12",
    "flat-16": "F16",
    "h16": "H16",
}

# URL fragments that indicate a fuel-type modifier (not a standalone engine model).
_FUEL_TYPE_URLS: dict[str, str] = {
    "diesel_engine": "diesel",
    "diesel fuel": "diesel",
}

# URL fragments that indicate the link describes only a modifier (fuel type or induction),
# not an engine model.  When a segment contains only such a link it should be treated as
# a modifier to the preceding engine rather than a new engine entry.
_MODIFIER_ONLY_URLS: frozenset[str] = frozenset(
    {
        "diesel_engine",
        "supercharger",
        "supercharged",
        "turbocharger",
        "turbocharging",
        "gas_turbine",
    },
)

# Compiled pattern for detecting a 3-digit CSS hex colour (after lower-casing).
_CSS_3DIGIT_HEX_RE = re.compile(r"^#[0-9a-f]{3}$")


def _expand_hex_shorthand(color: str) -> str:
    """Expand a CSS 3-digit hex colour to its 6-digit equivalent.

    Examples::

        "#fcc" → "#ffcccc"
        "#abc" → "#aabbcc"
        "#ffcccc" → "#ffcccc"  (unchanged)

    Args:
        color: Lower-cased, space-stripped colour string.

    Returns:
        6-digit hex colour string, or the original string if it was not a
        3-digit shorthand.
    """
    if _CSS_3DIGIT_HEX_RE.match(color):
        return "#" + "".join(c * 2 for c in color[1:])
    return color


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
        bg_lower = _expand_hex_shorthand(bg_lower)
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
                turbocharged,
                supercharged,
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
            supercharged,
            turbocharged,
            gas_turbine,
            fuel_type,
        )

    # ------------------------------------------------------------------
    # private helpers for parse_segment
    # ------------------------------------------------------------------

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
            any(mod in url for mod in _MODIFIER_ONLY_URLS) for url in all_link_urls
        ):
            return None

        fuel_type: str | None = None
        supercharged = False
        turbocharged = False
        gas_turbine = False
        for link in links:
            url = (link.get("url") or "").lower()
            for url_key, ftype in _FUEL_TYPE_URLS.items():
                if url_key in url:
                    fuel_type = ftype
            if "supercharger" in url or "supercharged" in url:
                supercharged = True
            if "turbocharger" in url or "turbocharging" in url:
                turbocharged = True
            if "gas_turbine" in url:
                gas_turbine = True

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
        if first_link_text and _EXACT_TYPE_RE.match(first_link_text):
            special_tokens.add(first_link_text)
            return first_link_text, None, ""

        type_str: str | None = None
        if first_link_text:
            m = _AFTER_DISPLACEMENT_TYPE_RE.search(first_link_text)
            if m:
                type_str = m.group(1)
        return type_str, first_link, first_link_text

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

            if type_str is None:
                type_str = EngineParsingHelpers._extract_type_from_link(
                    link_text,
                    special_tokens,
                )
                if type_str is None:
                    m = _AFTER_DISPLACEMENT_TYPE_RE.search(link_text)
                    if m:
                        type_str = m.group(1)

            if type_str is not None:
                m_mod = _TYPE_WITH_MODIFIER_RE.match(type_str)
                if m_mod:
                    modifier = m_mod.group(2).lower()
                    if modifier == "t":
                        turbocharged = True
                    elif modifier == "s":
                        supercharged = True
                    type_str = m_mod.group(1)

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
                for url_key, ftype in _FUEL_TYPE_URLS.items():
                    if url_key in url:
                        fuel_type = ftype
                        special_tokens.add(link_text)
                        break

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
        if _EXACT_TYPE_RE.match(link_text):
            special_tokens.add(link_text)
            return link_text

        m_mod = _TYPE_WITH_MODIFIER_RE.match(link_text)
        if m_mod:
            special_tokens.add(link_text)
            return link_text  # modifier stripping happens in caller

        verbose_key = link_text.lower()
        if verbose_key in _VERBOSE_TYPE_MAP:
            special_tokens.add(link_text)
            return _VERBOSE_TYPE_MAP[verbose_key]

        return None

    @staticmethod
    def _fallback_type_from_text(
        text: str,
        type_str: str | None,
        turbocharged: bool,
        supercharged: bool,
    ) -> tuple[str | None, bool, bool]:
        """Scan plain segment text for a type code when no link provided one.

        Returns ``(type_str, turbocharged, supercharged)``.
        """
        if type_str is not None:
            return type_str, turbocharged, supercharged

        m_plain = _PLAIN_TEXT_TYPE_RE.search(text)
        if not m_plain:
            return None, turbocharged, supercharged

        candidate = m_plain.group(1)
        m_mod = _TYPE_WITH_MODIFIER_RE.match(candidate)
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

        after_link = text[pos + len(first_link_text) :]
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
    def parse_layout_and_cylinders(
        type_str: str | None,
    ) -> tuple[str | None, int | None]:
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
