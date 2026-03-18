from bs4 import Tag

from scrapers.wiki.parsers.constants import BASE_COMMON_ALIASES
from scrapers.wiki.parsers.constants import CURRENT_CONSTRUCTORS_ID
from scrapers.wiki.parsers.sections.contants import TOP_SECTION_NAME
from scrapers.wiki.parsers.sections.data_classes import SectionProfile
from scrapers.wiki.parsers.sections.normalization import normalize_section_profile_key


def _split_into_parts(
    children: list[Tag],
    heading_class: str,
) -> list[tuple[str, str | None, list[Tag]]]:
    """Dzieli listę elementów na części według nagłówków danego poziomu."""
    parts: list[tuple[str, str | None, list[Tag]]] = []
    current_name: str = TOP_SECTION_NAME
    current_anchor: str | None = None
    current_elements: list[Tag] = []

    for child in children:
        if not isinstance(child, Tag):
            continue
        classes = child.get("class") or []
        if heading_class in classes:
            parts.append((current_name, current_anchor, current_elements))
            heading_tag = child.find(name=True, recursive=False)
            current_anchor = heading_tag.get("id") if heading_tag else None
            current_name = (
                heading_tag.get_text(" ", strip=True)
                if heading_tag
                else TOP_SECTION_NAME
            )
            current_elements = []
        else:
            current_elements.append(child)

    parts.append((current_name, current_anchor, current_elements))
    return parts



def _domain_aliases() -> dict[str, dict[str, set[str]]]:
    return {
        "seasons": {
            "results": {"grands prix", "results and standings"},
            "regulation changes": {"rule changes"},
            "mid-season changes": {"driver changes"},
        },
        "drivers": {
            "career results": {"racing record", "karting record"},
            "racing record": {"motorsport career results"},
            "non-championship": {"non-championship races"},
        },
        "circuits": {
            "circuits": {"formula one circuits", "list of formula one circuits"},
            "results": {"race results"},
            "layout history": {"history"},
            "events": {"races"},
            "lap records": {"formula one lap records"},
        },
        "constructors": {
            "former constructors": {"defunct constructors"},
            "championship results": {"formula one/world championship results"},
            "complete formula one results": {"complete world championship results"},
        },
        "grands_prix": {},
    }


def _canonical_sections() -> dict[str, set[str]]:
    return {
        "drivers": {"career results", "racing record", "non-championship"},
        "constructors": {
            "history",
            "championship results",
            "complete formula one results",
            "former constructors",
        },
        "circuits": {"circuits", "layout history", "lap records", "events", "results"},
        "seasons": {
            "results",
            "regulation changes",
            "mid-season changes",
            "calendar",
            "standings",
        },
        "grands_prix": {"by year", "winners"},
    }


def _copy_common_aliases() -> dict[str, set[str]]:
    return {key: set(values) for key, values in BASE_COMMON_ALIASES.items()}


def _build_profile_aliases(
    *,
    domain: str,
    domain_aliases: dict[str, dict[str, set[str]]],
) -> dict[str, frozenset[str]]:
    aliases = _copy_common_aliases()
    for key, values in domain_aliases.get(domain, {}).items():
        aliases.setdefault(key, set()).update(values)
    return {key: frozenset(values) for key, values in aliases.items()}


def _build_domain_profile(
    *,
    domain: str,
    canonical_sections: set[str],
    domain_aliases: dict[str, dict[str, set[str]]],
) -> SectionProfile:
    return SectionProfile(
        domain=domain,
        canonical_section_ids=frozenset(canonical_sections),
        heading_aliases=_build_profile_aliases(
            domain=domain,
            domain_aliases=domain_aliases,
        ),
        required_sections=frozenset(),
        optional_sections=frozenset(canonical_sections),
    )


def _build_profiles() -> dict[str, SectionProfile]:
    canonical = _canonical_sections()
    domain_aliases = _domain_aliases()
    profiles: dict[str, SectionProfile] = {}

    for domain, canonical_sections in canonical.items():
        profiles[domain] = _build_domain_profile(
            domain=domain,
            canonical_sections=canonical_sections,
            domain_aliases=domain_aliases,
        )

    return profiles


DOMAIN_SECTION_PROFILES = _build_profiles()


def get_section_profile(domain: str | None) -> SectionProfile | None:
    if not domain:
        return None
    return DOMAIN_SECTION_PROFILES.get(domain)


def profile_aliases_for_target(target: str, *, domain: str | None) -> set[str]:
    profile = get_section_profile(domain)
    if not profile:
        return set()

    normalized_target = normalize_section_profile_key(target)
    aliases = set(profile.aliases_for(normalized_target))

    if domain == "constructors" and CURRENT_CONSTRUCTORS_ID.match(normalized_target):
        aliases.update(
            {
                "constructors for the current season",
                "current constructors",
                "constructors",
            },
        )

    return aliases


def profile_entry_aliases(
    domain: str,
    section_id: str,
    *fallback_aliases: str,
) -> tuple[str, ...]:
    profile = get_section_profile(domain)
    merged: list[str] = []
    seen: set[str] = set()

    def add(value: str) -> None:
        normalized = normalize_section_profile_key(value)
        if not normalized or normalized in seen:
            return
        seen.add(normalized)
        merged.append(value)

    for alias in fallback_aliases:
        add(alias)

    if profile:
        for alias in sorted(profile.aliases_for(section_id)):
            add(alias)

    return tuple(merged)
