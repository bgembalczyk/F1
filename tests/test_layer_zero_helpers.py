from pathlib import Path

import pytest

from layers.path_resolver import format_domain_year_name
from layers.zero.run_profile_paths import layer_zero_raw_paths


def test_layer_zero_raw_paths_returns_json_path_only_when_csv_missing() -> None:
    json_path, csv_path = layer_zero_raw_paths(
        output_category="drivers",
        rendered_json_path="drivers.json",
        csv_output_path=None,
    )

    assert json_path == Path("layers/0_layer/drivers/A_scrape/drivers.json")
    assert csv_path is None


def test_layer_zero_raw_paths_returns_json_and_csv_paths() -> None:
    json_path, csv_path = layer_zero_raw_paths(
        output_category="circuits",
        rendered_json_path="circuits.json",
        csv_output_path="circuits.csv",
    )

    assert json_path == Path("layers/0_layer/circuits/A_scrape/circuits.json")
    assert csv_path == Path("layers/0_layer/circuits/A_scrape/circuits.csv")


def test_layer_zero_raw_paths_uses_only_filename_for_nested_inputs() -> None:
    json_path, csv_path = layer_zero_raw_paths(
        output_category="seasons",
        rendered_json_path="foo/bar/seasons.json",
        csv_output_path="deep/nested/seasons.csv",
    )

    assert json_path == Path("layers/0_layer/seasons/A_scrape/seasons.json")
    assert csv_path == Path("layers/0_layer/seasons/A_scrape/seasons.csv")


def test_layer_zero_raw_paths_rejects_empty_filename() -> None:
    with pytest.raises(ValueError, match="cannot be empty"):
        layer_zero_raw_paths(
            output_category="drivers",
            rendered_json_path="",
            csv_output_path=None,
        )


def test_layer_zero_raw_paths_rejects_double_extension() -> None:
    with pytest.raises(ValueError, match="duplicated extension"):
        layer_zero_raw_paths(
            output_category="drivers",
            rendered_json_path="drivers.json.json",
            csv_output_path=None,
        )


def test_format_domain_year_name_supports_domain_and_year_placeholders() -> None:
    assert (
        format_domain_year_name(
            "{domain}_summary_{year}.json",
            domain="teams",
            year=2026,
        )
        == "teams_summary_2026.json"
    )
