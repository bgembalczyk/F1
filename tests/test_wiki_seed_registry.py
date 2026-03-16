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
    assert payload["default_output_path"].startswith("drivers/")
    assert "F1DriversListScraper" in serialized


def test_wiki_list_job_registry_integrity() -> None:
    validate_list_job_registry(WIKI_LIST_JOB_REGISTRY)


def test_list_job_registry_entry_serialization() -> None:
    entry = WIKI_LIST_JOB_REGISTRY[0]

    payload = entry.to_dict()
    serialized = json.dumps(payload, default=str)

    assert isinstance(entry, ListJobRegistryEntry)
    assert payload["output_category"] == "circuits"
    assert payload["json_output_path"].startswith("circuits/")
    assert "CircuitsListScraper" in serialized
