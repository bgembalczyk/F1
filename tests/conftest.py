from __future__ import annotations

import re
from pathlib import Path

import pytest

FAST_PROFILE_EXCLUDE_PATTERNS: tuple[str, ...] = (
    "/tests/contract/test_dsl_contract.py",
    "/tests/contract/test_minimal_fetch_contract.py",
)

_MARKER_BY_PATTERN: tuple[tuple[str, str], ...] = (
    # Legacy compatibility suites kept outside unit/contract/architecture profile.
    ("/contract/test_dsl_contract", "integration"),
    ("/contract/test_minimal_fetch_contract", "integration"),
    ("tests/contract/", "contract"),
    ("tests/architecture/", "architecture"),
    ("/test_architecture_", "architecture"),
    ("/test_domain_entrypoint_boundaries", "architecture"),
    ("/test_section_architecture_boundaries", "architecture"),
    ("/test_domain_minimal_e2e", "integration"),
    ("/test_driver_infobox_integration", "integration"),
    ("/test_section_adapter_integration", "integration"),
    ("/test_common_value_objects_integration", "integration"),
    ("/test_cli_entrypoints_contract", "integration"),
    ("/test_constructor_column", "integration"),
    ("/test_drivers_checkpoint_flow", "integration"),
    ("/test_helpers_normalization", "integration"),
    ("/test_main_layer_zero_merge", "integration"),
    ("/test_naming_conventions", "integration"),
    ("/test_record_factories", "integration"),
    ("/test_records", "integration"),
    ("/test_scraper_config", "integration"),
    ("/test_scraper_record_factories", "integration"),
    ("/test_season_service_to_range", "integration"),
    ("/test_seed_l0", "integration"),
    ("/test_seed_section_orchestration_flow", "integration"),
    ("/test_single_circuit_scraper", "integration"),
    ("/test_validators", "integration"),
    ("/test_validators_additional", "integration"),
    ("/test_value_objects", "integration"),
    ("/test_wiki_application", "integration"),
    ("/test_wiki_seed_registry", "integration"),
    ("/test_circuit_parsers", "integration"),
    ("/test_cli_bootstrap_boundaries", "integration"),
    ("/test_cli_deprecation_runtime", "integration"),
    ("/test_complete_extractor_base", "integration"),
    ("/test_composite_record_validator", "integration"),
    ("/test_domain_section_decomposition", "integration"),
    ("/test_driver_infobox_parsers", "integration"),
    ("/test_formatters", "integration"),
    ("/test_grands_prix_columns", "integration"),
    ("/test_http_clients", "integration"),
    ("/test_models", "integration"),
    ("/test_points_cli_bootstrap_contract", "integration"),
    ("/test_post_process", "integration"),
    ("/test_quality_reporter_contract", "integration"),
    ("/test_record_types", "integration"),
    ("/test_red_flagged_races_scraper", "integration"),
    ("/test_schema_engine_regression", "integration"),
    ("/test_scraper_contract", "integration"),
    ("/test_scraper_errors", "integration"),
    ("/test_scraper_options", "integration"),
    ("/test_section_parser_ci_meta", "integration"),
    ("/test_section_parser_regressions", "integration"),
    ("/test_services", "integration"),
    ("/test_single_constructor_scraper", "integration"),
    ("/test_single_scraper_components_and_orchestration", "integration"),
    ("/test_table_pipeline", "integration"),
    ("/test_table_scraper_options", "integration"),
)


def marker_for_path(path: str) -> str:
    """Map test file path to a run-profile marker.

    Konwencja markerów przypisuje dokładnie jeden marker profilowy na plik:
    - ``contract``: pliki pod ``tests/contract``;
    - ``architecture``: testy architektoniczne (katalog + nazwy plików);
    - ``integration``: testy integracyjne/E2E po nazwie pliku;
    - ``unit``: domyślnie dla pozostałych testów.
    """

    normalized = path.replace("\\", "/")
    if "/tests/" in normalized:
        normalized = normalized[normalized.index("/tests/") + 1 :]

    if not normalized.startswith("tests/"):
        return "unit"

    path_with_leading_slash = f"/{normalized}"
    for pattern, marker in _MARKER_BY_PATTERN:
        if pattern in normalized or pattern in path_with_leading_slash:
            return marker

    file_name = Path(normalized).name
    if file_name.startswith("test_integration_") or file_name.endswith(
        "_integration.py",
    ):
        return "integration"
    return "unit"


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        marker = marker_for_path(str(Path(item.fspath)))
        item.add_marker(getattr(pytest.mark, marker))


def selected_profile_markers(markexpr: str) -> set[str]:
    """Return explicitly requested profile markers from ``-m`` expression."""

    if not markexpr.strip():
        return set()
    return {
        token.lower()
        for token in re.findall(
            r"\b(unit|contract|architecture|integration)\b",
            markexpr,
            flags=re.IGNORECASE,
        )
    }


def pytest_ignore_collect(
    collection_path: Path,
    config: pytest.Config,
) -> bool:
    """Skip collecting files outside selected profile markers.

    This avoids importing tests from unrelated profiles when running with ``-m``.
    """

    if collection_path.suffix != ".py":
        return False

    selected_markers = selected_profile_markers(config.option.markexpr or "")
    if not selected_markers:
        return False

    normalized = str(collection_path).replace("\\", "/")
    if {"unit", "contract", "architecture"}.issubset(selected_markers) and any(
        pattern in normalized for pattern in FAST_PROFILE_EXCLUDE_PATTERNS
    ):
        return True

    marker = _marker_for_path(str(collection_path))
    return marker not in selected_markers
