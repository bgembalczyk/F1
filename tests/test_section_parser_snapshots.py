from __future__ import annotations

from bs4 import BeautifulSoup
import pytest

from scrapers.wiki.parsers.content_text import ContentTextParser
from tests._section_parser_fixture_pattern import SNAPSHOT_CASES_BY_DOMAIN
from tests._section_parser_fixture_pattern import iter_snapshot_cases


def _parse_sections(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    parsed = ContentTextParser().parse(soup.find("div", id="mw-content-text"))
    return parsed["sections"]


def _snapshot_payload(sections: list[dict]) -> list[dict]:
    payload = []
    for section in sections:
        payload.append(
            {
                "name": section["name"],
                "section_id": section["section_id"],
                "kinds": [
                    el["kind"]
                    for sub in section.get("sub_sections", [])
                    for s2 in sub.get("sub_sub_sections", [])
                    for s3 in s2.get("sub_sub_sub_sections", [])
                    for el in s3.get("elements", [])
                ],
            }
        )
    return payload


@pytest.mark.parametrize("fixture", iter_snapshot_cases(), ids=lambda case: f"{case.domain}-{case.variant}")
def test_snapshot_section_parser_contract_per_domain(fixture) -> None:
    snapshot = _snapshot_payload(_parse_sections(fixture.html))

    assert snapshot[1]["section_id"] == fixture.expected_section_id
    assert fixture.expected_kind in snapshot[1]["kinds"]


def test_snapshot_matrix_covers_new_parser_domains() -> None:
    assert {"constructors", "circuits", "seasons"}.issubset(SNAPSHOT_CASES_BY_DOMAIN)
    for domain in ("constructors", "circuits", "seasons"):
        variants = {fixture.variant for fixture in SNAPSHOT_CASES_BY_DOMAIN[domain]}
        assert variants == {"minimal", "edge"}
