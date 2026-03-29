from scrapers.base.orchestration.components import SectionSourceAdapter


def test_components_public_api_exposes_section_source_adapter() -> None:
    assert SectionSourceAdapter.__name__ == "SectionSourceAdapter"
