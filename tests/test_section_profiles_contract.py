# ruff: noqa: PLR2004
from __future__ import annotations

from bs4 import BeautifulSoup

from scrapers.wiki.parsers.sections.adapter import find_section_tree
from scrapers.wiki.parsers.sections.detection import find_section_heading
from scrapers.wiki.parsers.sections.helpers import DOMAIN_SECTION_PROFILES
from scrapers.wiki.parsers.sections.helpers import profile_aliases_for_target
from scrapers.wiki.parsers.sections.helpers import profile_entry_aliases


def test_section_profiles_define_expected_domains_and_contract_shape() -> None:
    expected = {"drivers", "constructors", "circuits", "seasons", "grands_prix"}

    assert expected.issubset(DOMAIN_SECTION_PROFILES)
    for domain in expected:
        profile = DOMAIN_SECTION_PROFILES[domain]
        assert profile.domain == domain
        assert isinstance(profile.canonical_section_ids, frozenset)
        assert profile.priorities.exact_id_score > profile.priorities.exact_text_score
        assert profile.priorities.fuzzy_threshold >= 0.8


def test_section_profile_aliases_resolve_canonical_heading_in_detection() -> None:
    html = '<h2><span class="mw-headline">Rule changes</span></h2>'
    soup = BeautifulSoup(html, "html.parser")

    match = find_section_heading(soup, "Regulation_changes", domain="seasons")

    assert match is not None
    assert match.strategy in {"exact_text", "fuzzy"}


def test_section_profile_aliases_resolve_canonical_heading_in_tree_adapter() -> None:
    article = {
        "sections": [
            {
                "name": "Rule changes",
                "section_id": "rule_changes",
                "elements": [],
                "sub_sections": [],
            },
        ],
    }

    section = find_section_tree(article, "Regulation_changes", domain="seasons")

    assert section is not None
    assert section["section_id"] == "rule_changes"


def test_profile_entry_aliases_merges_fallback_and_profile_aliases_stably() -> None:
    aliases = profile_entry_aliases("circuits", "layout_history", "Layout_history")

    normalized = {alias.lower().replace("_", " ") for alias in aliases}
    assert "layout history" in normalized
    assert "history" in normalized


def test_profile_aliases_for_target_supports_dynamic_current_constructors() -> None:
    aliases = profile_aliases_for_target(
        "Constructors_for_the_2026_season",
        domain="constructors",
    )

    normalized = {alias.lower().replace("_", " ") for alias in aliases}
    assert "constructors for the current season" in normalized
    assert "current constructors" in normalized
    assert "constructors" in normalized
