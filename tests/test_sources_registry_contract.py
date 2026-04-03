import warnings

import pytest

from scrapers.wiki.sources_registry import get_source_by_seed_name
from scrapers.wiki.sources_registry import get_source_by_source_name
from scrapers.wiki.sources_registry import resolve_seed_name
from scrapers.wiki.sources_registry import validate_sources_registry_consistency


def test_sources_registry_consistency_validation_passes_for_canonical_registry() -> (
    None
):
    validate_sources_registry_consistency()


def test_sources_registry_exposes_single_source_definition_fields() -> None:
    source = get_source_by_seed_name("drivers", warn=False)
    assert source.domain == "drivers"
    assert source.seed_name == "drivers"
    assert source.source_name == "drivers"
    assert source.output_file == "f1_drivers.json"
    assert source.profile == "list_scraper"


def test_get_source_by_source_name_resolves_canonical_entries() -> None:
    source = get_source_by_source_name("points_sprint")
    assert source.seed_name == "points_sprint"


def test_legacy_seed_alias_logs_and_emits_deprecation_warning(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", DeprecationWarning)
        resolved = resolve_seed_name("constructors", warn=True)

    assert resolved == "constructors_current"
    assert any(item.category is DeprecationWarning for item in caught)
    assert "deprecated" in caplog.text
