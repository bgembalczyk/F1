"""Engine text parsing helpers.

This module contains helpers for extracting displacement, type codes,
model names and layout information from raw engine description text.
Extracted from engine_parsing.py to follow SRP.

Follows SOLID principles:
- Single Responsibility: Handles only text-based engine property extraction
- High Cohesion: All methods work together to parse plain text into engine metadata
- Information Expert: Text parsing logic grouped with text data
"""

import re

from scrapers.base.helpers.parsing import parse_float_from_text
from scrapers.base.table.columns.helpers.constants import CC_TO_L_THRESHOLD
from scrapers.base.table.columns.helpers.constants import DISPLACEMENT_RE
from scrapers.base.table.columns.helpers.constants import FORMULA_CLASS_TYPE_CODES
from scrapers.base.table.columns.helpers.constants import PLAIN_TEXT_TYPE_RE
from scrapers.base.table.columns.helpers.constants import TYPE_WITH_MODIFIER_RE


class EngineTextHelpers:
    """
    Helper class for extracting engine properties from raw text.

    Provides methods for:
    - Extracting displacement values
    - Extracting model names and suffixes
    - Inferring engine type from plain text when no link is available
    - Parsing layout letter and cylinder count from type strings
    """

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
        return EngineTextHelpers._strip_special_suffix_tokens(
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
            return EngineTextHelpers._trim_text_before_displacement(text)

        pos = text.find(first_link_text)
        if pos < 0:
            return first_link_text

        after_link = text[pos + len(first_link_text) :]
        if not after_link.strip():
            return EngineTextHelpers._trim_text_before_displacement(first_link_text)

        model_suffix = EngineTextHelpers._extract_model_suffix(
            after_link,
            special_tokens,
        )
        if not model_suffix:
            return first_link_text
        return f"{first_link_text} {model_suffix}"

    @staticmethod
    def fallback_type_from_text(
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
        if candidate.upper() in FORMULA_CLASS_TYPE_CODES:
            return None, turbocharged, supercharged
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
