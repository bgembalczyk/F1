"""Engine link parsing helpers.

This module contains helpers for resolving engine type codes,
modifier flags and model links from HTML anchor elements.
Extracted from engine_parsing.py to follow SRP.

Follows SOLID principles:
- Single Responsibility: Handles only link-related engine parsing
- High Cohesion: All methods work together to resolve links into engine metadata
- Information Expert: Link parsing logic grouped with link data
"""

from models.records.link import LinkRecord
from scrapers.base.table.columns.helpers.constants import AFTER_DISPLACEMENT_TYPE_RE
from scrapers.base.table.columns.helpers.constants import EXACT_TYPE_RE
from scrapers.base.table.columns.helpers.constants import FUEL_TYPE_URLS
from scrapers.base.table.columns.helpers.constants import MODIFIER_ONLY_URLS
from scrapers.base.table.columns.helpers.constants import TYPE_WITH_MODIFIER_RE
from scrapers.base.table.columns.helpers.constants import VERBOSE_TYPE_MAP
from scrapers.base.table.columns.helpers.link_lookup import build_link_lookup


class EngineLinkHelpers:
    """
    Helper class for resolving engine metadata from HTML link elements.

    Provides methods for:
    - Building engine link lookups
    - Extracting modifier flags (turbocharged, supercharged, etc.)
    - Resolving engine type codes from links
    - Processing secondary (non-model) links
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
        return build_link_lookup(links)

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
    def try_modifier_only_segment(
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
            EngineLinkHelpers._extract_modifier_flags(links)
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
    def resolve_first_link_type(
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
    def _update_type_from_link_text(
        link_text: str,
        type_str: str | None,
        special_tokens: set[str],
    ) -> str | None:
        """Update type string from link text if no type has been resolved yet."""
        if type_str is not None:
            return type_str

        extracted_type = EngineLinkHelpers._extract_type_from_link(
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
    def process_secondary_links(
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

            type_str = EngineLinkHelpers._update_type_from_link_text(
                link_text,
                type_str,
                special_tokens,
            )
            type_str, supercharged, turbocharged = (
                EngineLinkHelpers._strip_type_modifier(
                    type_str,
                    supercharged=supercharged,
                    turbocharged=turbocharged,
                )
            )
            supercharged, turbocharged, gas_turbine, fuel_type = (
                EngineLinkHelpers._update_modifiers_from_url(
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
