from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup
import pytest

from scrapers.base.post_processors import CommonMetadataPostProcessor
from scrapers.base.post_processors import apply_post_processors
from scrapers.wiki.parsers.content_text import ContentTextParser
from scrapers.wiki.parsers.elements.infobox import InfoboxParser

FIXTURE_DIR = Path("tests/fixtures/e2e_html")
SNAPSHOT_DIR = Path("tests/fixtures/e2e_snapshots")
DOMAINS = ("drivers", "constructors", "circuits", "seasons", "grands_prix")
SCRAPED_AT = datetime(2026, 1, 1, 0, 0, 0)


@pytest.mark.parametrize("domain", DOMAINS)
def test_domain_minimal_e2e_snapshot_contract(domain: str) -> None:
    html = (FIXTURE_DIR / f"{domain}.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    table_link = soup.select_one("table.wikitable a")
    assert table_link is not None
    seed_input = [{"name": table_link.get_text(strip=True), "link": table_link.get("href")}]

    seed_records = [
        {
            "name": seed_input[0]["name"],
            "link": seed_input[0]["link"],
            "source_url": f"https://example.test/{domain}",
            "scraped_at": SCRAPED_AT.isoformat(),
        }
    ]

    content = soup.find("div", id="mw-content-text")
    assert content is not None
    sections = ContentTextParser().parse(content)["sections"]
    section_record = {
        "section_label": sections[1]["section_label"],
        "section_id": sections[1]["section_id"],
    }

    infobox = soup.find("table", class_=lambda c: c and "infobox" in c)
    assert infobox is not None
    infobox_record = InfoboxParser().parse(infobox)

    post_records = apply_post_processors(
        [
            CommonMetadataPostProcessor(
                source_url=f"https://example.test/{domain}",
                section_id=section_record["section_id"],
                scraped_at=SCRAPED_AT,
            ),
        ],
        [{"domain": domain, "url": f"https://example.test/{domain}"}],
    )

    payload = {
        "domain": domain,
        "seed_record": {
            "name": seed_records[0]["name"],
            "link": seed_records[0]["link"],
            "source_url": seed_records[0]["source_url"],
            "scraped_at": seed_records[0]["scraped_at"],
        },
        "section_record": section_record,
        "infobox_record": {
            "title": infobox_record["title"],
            "rows": infobox_record["rows"],
        },
        "postprocess_record": post_records[0],
    }

    snapshot_path = SNAPSHOT_DIR / f"{domain}.json"
    expected = json.loads(snapshot_path.read_text(encoding="utf-8"))
    assert payload == expected
