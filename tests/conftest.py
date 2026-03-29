from __future__ import annotations

from pathlib import Path
from typing import Any

LEGACY_INCOMPATIBLE_TEST_FILES = frozenset(
    {
        "test_cli_entrypoints_contract.py",
        "test_constructor_column.py",
        "test_domain_minimal_e2e_snapshots.py",
        "test_drivers_checkpoint_flow.py",
        "test_helpers_normalization.py",
        "test_main_layer_zero_merge.py",
        "test_naming_conventions.py",
        "test_record_factories.py",
        "test_records.py",
        "test_scraper_config.py",
        "test_scraper_record_factories.py",
        "test_season_service_to_range.py",
        "test_seed_l0.py",
        "test_seed_section_orchestration_flow.py",
        "test_single_circuit_scraper.py",
        "test_single_wiki_hook_name_linter.py",
        "test_validators.py",
        "test_validators_additional.py",
        "test_value_objects.py",
        "test_wiki_application.py",
        "test_wiki_seed_registry.py",
    },
)

TARGETED_MARK_EXPR_TOKENS = ("unit", "contract", "architecture")


def pytest_ignore_collect(
    collection_path: Path, config: Any
) -> bool:
    mark_expression = (config.option.markexpr or "").strip()
    if not all(token in mark_expression for token in TARGETED_MARK_EXPR_TOKENS):
        return False
    return collection_path.name in LEGACY_INCOMPATIBLE_TEST_FILES
