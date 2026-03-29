# ruff: noqa: E501, PT007
import json

import pytest

from layers.seed.registry import WIKI_LIST_JOB_REGISTRY
from layers.seed.registry import WIKI_SEED_REGISTRY
from layers.seed.registry import ListJobRegistryEntry
from layers.seed.registry import SeedRegistryEntry
from layers.seed.registry import validate_list_job_registry
from layers.seed.registry import validate_seed_registry


def _seed_registry_validation_negative_cases() -> tuple[object, ...]:
    return (
        pytest.param(
            lambda: (
                SeedRegistryEntry(
                    seed_name="empty-url",
                    wikipedia_url="",
                    output_category="drivers",
                    list_scraper_cls=object,
                    default_output_path="raw/drivers/a.json",
                    legacy_output_path="drivers/a.json",
                ),
            ),
            validate_seed_registry,
            "Seed 'empty-url' has empty wikipedia_url",
            id="seed_registry_empty_url",
        ),
        pytest.param(
            lambda: (
                SeedRegistryEntry(
                    seed_name="bad-json-path",
                    wikipedia_url="https://example.test/a",
                    output_category="drivers",
                    list_scraper_cls=object,
                    default_output_path="raw/circuits/a.json",
                    legacy_output_path="drivers/a.json",
                ),
            ),
            validate_seed_registry,
            "Seed 'bad-json-path' has inconsistent output path 'raw/circuits/a.json' for category 'drivers'",
            id="seed_registry_invalid_json_path_prefix",
        ),
        pytest.param(
            lambda: (
                SeedRegistryEntry(
                    seed_name="bad-legacy-path",
                    wikipedia_url="https://example.test/a",
                    output_category="drivers",
                    list_scraper_cls=object,
                    default_output_path="raw/drivers/a.json",
                    legacy_output_path="circuits/a.json",
                ),
            ),
            validate_seed_registry,
            "Seed 'bad-legacy-path' has inconsistent legacy output path 'circuits/a.json' for category 'drivers'",
            id="seed_registry_invalid_legacy_path_prefix",
        ),
    )


def _list_registry_validation_negative_cases() -> tuple[object, ...]:
    return (
        pytest.param(
            lambda: (
                ListJobRegistryEntry(
                    seed_name="empty-url",
                    wikipedia_url="",
                    output_category="drivers",
                    list_scraper_cls=object,
                    json_output_path="raw/drivers/list/a.json",
                    legacy_json_output_path="drivers/a.json",
                ),
            ),
            validate_list_job_registry,
            "List seed 'empty-url' has empty wikipedia_url",
            id="list_registry_empty_url",
        ),
        pytest.param(
            lambda: (
                ListJobRegistryEntry(
                    seed_name="bad-json-path",
                    wikipedia_url="https://example.test/a",
                    output_category="drivers",
                    list_scraper_cls=object,
                    json_output_path="raw/circuits/list/a.json",
                    legacy_json_output_path="drivers/a.json",
                ),
            ),
            validate_list_job_registry,
            "List seed 'bad-json-path' has inconsistent output path 'raw/circuits/list/a.json' for category 'drivers'",
            id="list_registry_invalid_json_path_prefix",
        ),
        pytest.param(
            lambda: (
                ListJobRegistryEntry(
                    seed_name="bad-legacy-path",
                    wikipedia_url="https://example.test/a",
                    output_category="drivers",
                    list_scraper_cls=object,
                    json_output_path="raw/drivers/list/a.json",
                    legacy_json_output_path="circuits/a.json",
                ),
            ),
            validate_list_job_registry,
            "List seed 'bad-legacy-path' has inconsistent legacy output path 'circuits/a.json' for category 'drivers'",
            id="list_registry_invalid_legacy_path_prefix",
        ),
    )


def _registry_validation_negative_cases() -> tuple[object, ...]:
    return (
        *_seed_registry_validation_negative_cases(),
        *_list_registry_validation_negative_cases(),
    )


@pytest.mark.parametrize(
    ("registry_factory", "validator", "expected_message"),
    _registry_validation_negative_cases(),
)
def test_registry_validation_negative_cases(
    registry_factory,
    validator,
    expected_message,
) -> None:
    with pytest.raises(ValueError, match=expected_message):
        validator(registry_factory())


def test_wiki_seed_registry_integrity() -> None:
    validate_seed_registry(WIKI_SEED_REGISTRY)


def test_seed_registry_entry_serialization() -> None:
    entry = WIKI_SEED_REGISTRY[0]

    payload = entry.to_dict()
    serialized = json.dumps(payload, default=str)

    assert isinstance(entry, SeedRegistryEntry)
    assert payload["seed_name"] == "drivers"
    assert payload["wikipedia_url"].startswith("https://")
    assert payload["output_category"] == "drivers"
    assert payload["default_output_path"].startswith("raw/drivers/")
    assert payload["legacy_output_path"].startswith("drivers/")
    assert "F1DriversListScraper" in serialized


def test_wiki_list_job_registry_integrity() -> None:
    validate_list_job_registry(WIKI_LIST_JOB_REGISTRY)


def test_list_job_registry_entry_serialization() -> None:
    entry = WIKI_LIST_JOB_REGISTRY[0]

    payload = entry.to_dict()
    serialized = json.dumps(payload, default=str)

    assert isinstance(entry, ListJobRegistryEntry)
    assert payload["output_category"] == "circuits"
    assert payload["wikipedia_url"].startswith("https://")
    assert payload["json_output_path"].startswith("raw/circuits/")
    assert payload["legacy_json_output_path"].startswith("circuits/")
    assert "CircuitsListScraper" in serialized


def test_wiki_list_job_registry_contains_expected_layer_zero_jobs() -> None:
    jobs_by_seed = {entry.seed_name: entry for entry in WIKI_LIST_JOB_REGISTRY}

    assert (
        jobs_by_seed["seasons"].json_output_path == "raw/seasons/list/f1_seasons.json"
    )
    assert (
        jobs_by_seed["grands_prix_by_title"].json_output_path
        == "raw/grands_prix/list/f1_grands_prix_by_title.json"
    )
    assert jobs_by_seed["engines_regulations"].output_category == "rules"
    assert jobs_by_seed["engines_restrictions"].output_category == "rules"
    assert (
        jobs_by_seed["grands_prix_red_flagged_non_championship"].output_category
        == "races"
    )
    assert (
        jobs_by_seed["grands_prix_red_flagged_world_championship"].output_category
        == "races"
    )
    assert jobs_by_seed["sponsorship_liveries"].output_category == "teams"
    assert jobs_by_seed["constructors_privateer"].output_category == "teams"
    assert jobs_by_seed["constructors_former"].output_category == "chassis_constructors"
    assert (
        jobs_by_seed["constructors_indianapolis_only"].output_category
        == "chassis_constructors"
    )
    assert jobs_by_seed["tyres"].output_category == "seasons"
