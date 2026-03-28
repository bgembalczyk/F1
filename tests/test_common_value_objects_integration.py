from __future__ import annotations

from scrapers.base.sections.interface import SectionParseResult
from scrapers.base.sections.serializer import serialize_section_result


def test_section_parse_result_serialization_exports_legacy_json_strings() -> None:
    payload = serialize_section_result(
        SectionParseResult(
            section_id=" Career Results ",
            section_label="  Career   Results ",
            records=[{"year": 1950}],
            metadata={},
        ),
    )

    assert payload["section_id"] == "career_results"
    assert payload["section_label"] == "Career Results"
    assert payload["metadata"]["section_id"] == "career_results"
    assert payload["metadata"]["section_label"] == "Career Results"
