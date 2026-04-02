from scrapers.cli import build_pipeline_spec_debug_output
from scrapers.wiki.pipeline_spec import get_pipeline_spec_for_domain
from scrapers.wiki.pipeline_spec import validate_wiki_pipeline_spec


def test_pipeline_spec_validation_passes() -> None:
    validate_wiki_pipeline_spec()


def test_pipeline_spec_includes_transformers_and_postprocess_for_domain() -> None:
    drivers_spec = get_pipeline_spec_for_domain("drivers")

    assert drivers_spec is not None
    assert "drivers_domain" in drivers_spec.transformers
    assert "merge_duplicate_drivers" in drivers_spec.postprocess


def test_cli_builds_debug_output_from_pipeline_spec() -> None:
    payload = build_pipeline_spec_debug_output()

    assert "drivers" in payload
    assert "postprocess=merge_duplicate_drivers,sort_drivers_by_name" in payload
