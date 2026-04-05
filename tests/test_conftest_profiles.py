from __future__ import annotations

from tests import conftest as tests_conftest


def test_marker_for_path_maps_profiles_and_fallbacks() -> None:
    assert (
        tests_conftest._marker_for_path(
            "tests/contract/test_complete_extractor_children_contract.py",
        )
        == "contract"
    )
    assert (
        tests_conftest._marker_for_path("tests/contract/test_dsl_contract.py")
        == "integration"
    )
    assert (
        tests_conftest._marker_for_path("tests/test_architecture_import_rules.py")
        == "architecture"
    )
    assert (
        tests_conftest._marker_for_path(
            "tests/test_adr_enforcement_policy_integration.py",
        )
        == "integration"
    )
    assert (
        tests_conftest._marker_for_path("tests/test_integration_private_api_policy.py")
        == "integration"
    )
    assert tests_conftest._marker_for_path("tests/test_results.py") == "unit"


def test_selected_profile_markers_parses_only_supported_profiles() -> None:
    markexpr = "(unit or CONTRACT) and not smoke and integration"

    assert tests_conftest._selected_profile_markers(markexpr) == {
        "unit",
        "contract",
        "integration",
    }


def test_selected_profile_markers_returns_empty_set_for_blank_expression() -> None:
    assert tests_conftest._selected_profile_markers("   ") == set()
