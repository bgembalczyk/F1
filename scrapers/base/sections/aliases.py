from __future__ import annotations

import re

from scrapers.base.helpers.text import clean_wiki_text


def _normalize_section_text(text: str) -> str:
    return clean_wiki_text(text.replace("_", " ")).lower().strip()

COMMON_SECTION_ALIASES: dict[str, set[str]] = {
    "results": {"result", "results and standings", "grands prix"},
    "career results": {
        "racing record",
        "career record",
        "motorsport career results",
        "racing career",
    },
}

DOMAIN_SECTION_ALIASES: dict[str, dict[str, set[str]]] = {
    "seasons": {
        "results": {"grands prix", "results and standings"},
    },
    "drivers": {
        "career results": {"racing record", "karting record"},
    },
    "circuits": {
        "circuits": {"formula one circuits", "list of formula one circuits"},
        "results": {"race results"},
    },
    "constructors": {
        "former constructors": {"defunct constructors"},
    },
}

_CURRENT_CONSTRUCTORS_ID = re.compile(r"^constructors for the (\d{4}) season$")


def builtin_aliases_for_target(target: str, *, domain: str | None) -> set[str]:
    normalized_target = _normalize_section_text(target)
    aliases = set(COMMON_SECTION_ALIASES.get(normalized_target, set()))

    if domain:
        aliases.update(DOMAIN_SECTION_ALIASES.get(domain, {}).get(normalized_target, set()))
        aliases.update(_dynamic_domain_aliases(normalized_target, domain=domain))

    return aliases


def _dynamic_domain_aliases(normalized_target: str, *, domain: str) -> set[str]:
    if domain != "constructors":
        return set()

    if _CURRENT_CONSTRUCTORS_ID.match(normalized_target):
        return {
            "constructors for the current season",
            "current constructors",
            "constructors",
        }
    return set()
