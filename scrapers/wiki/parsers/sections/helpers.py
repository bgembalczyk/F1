from bs4 import Tag

from scrapers.wiki.parsers.constants import BASE_COMMON_ALIASES
from scrapers.wiki.parsers.constants import CURRENT_CONSTRUCTORS_ID
from scrapers.wiki.parsers.sections.constants import TOP_SECTION_NAME
from scrapers.wiki.parsers.sections.data_classes import SectionProfile
from scrapers.wiki.parsers.sections.normalization import normalize_section_profile_key
from scrapers.wiki.parsers.sections.section_profiles_config import SECTION_PROFILES_CONFIG
from scrapers.wiki.parsers.sections.section_profiles_config import validate_section_profiles_config


_HEADING_CLASS_TO_TAG = {
    "mw-heading2": "h2",
    "mw-heading3": "h3",
    "mw-heading4": "h4",
    "mw-heading5": "h5",
    "mw-heading6": "h6",
}


def _is_heading_marker(tag: Tag, heading_class: str) -> bool:
    classes = tag.get("class") or []
    if heading_class in classes:
        return True
    expected_tag = _HEADING_CLASS_TO_TAG.get(heading_class)
    return bool(expected_tag and tag.name == expected_tag)


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
        if _is_heading_marker(child, heading_class):
            parts.append((current_name, current_anchor, current_elements))
            heading_tag = child.find(name=True, recursive=False)
            if child.name in {"h2", "h3", "h4", "h5", "h6"}:
                heading_tag = child
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


def _copy_common_aliases() -> dict[str, set[str]]:
    return {key: set(values) for key, values in BASE_COMMON_ALIASES.items()}


def _build_profile_aliases(
    *,
    domain_aliases: dict[str, frozenset[str]],
) -> dict[str, frozenset[str]]:
    aliases = _copy_common_aliases()
    for key, values in domain_aliases.items():
        aliases.setdefault(key, set()).update(values)
    return {key: frozenset(values) for key, values in aliases.items()}


def _build_domain_profile(
    *,
    domain: str,
    canonical_sections: frozenset[str],
    domain_aliases: dict[str, frozenset[str]],
) -> SectionProfile:
    return SectionProfile(
        domain=domain,
        canonical_section_ids=frozenset(canonical_sections),
        heading_aliases=_build_profile_aliases(
            domain_aliases=domain_aliases,
        ),
        required_sections=frozenset(),
        optional_sections=frozenset(canonical_sections),
    )


def _build_profiles() -> dict[str, SectionProfile]:
    validate_section_profiles_config(SECTION_PROFILES_CONFIG)
    return {
        domain: _build_domain_profile(
            domain=domain,
            canonical_sections=config.canonical_sections,
            domain_aliases=dict(config.heading_aliases),
        )
        for domain, config in SECTION_PROFILES_CONFIG.items()
    }


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
