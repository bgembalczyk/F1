import json

from scrapers.wiki.seed_registry import WIKI_LIST_JOB_REGISTRY
from scrapers.wiki.seed_registry import WIKI_SEED_REGISTRY
from scrapers.wiki.seed_registry import ListJobRegistryEntry
from scrapers.wiki.seed_registry import SeedRegistryEntry
from scrapers.wiki.seed_registry import validate_list_job_registry
from scrapers.wiki.seed_registry import validate_seed_registry


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

    assert jobs_by_seed["seasons"].json_output_path == "raw/seasons/list/f1_seasons.json"
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
    assert jobs_by_seed["constructors_indianapolis_only"].output_category == "chassis_constructors"
    assert jobs_by_seed["tyres"].output_category == "seasons"


def test_layer_one_runner_map_is_complete_for_seed_registry() -> None:
    import datetime

    if not hasattr(datetime, "UTC"):
        datetime.UTC = datetime.timezone.utc

    from scrapers.wiki.orchestration import build_layer_one_runner_map

    runner_map = build_layer_one_runner_map()
    seed_names = {entry.seed_name for entry in WIKI_SEED_REGISTRY}

    assert set(runner_map) == seed_names
