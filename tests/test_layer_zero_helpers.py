from pathlib import Path

from layers.zero.run_profile_paths import layer_zero_raw_paths


def test_layer_zero_raw_paths_returns_json_path_only_when_csv_missing() -> None:
    json_path, csv_path = layer_zero_raw_paths(
        output_category="drivers",
        rendered_json_path="drivers.json",
        csv_output_path=None,
    )

    assert json_path == Path("layers/0_layer/drivers/raw/drivers.json")
    assert csv_path is None


def test_layer_zero_raw_paths_returns_json_and_csv_paths() -> None:
    json_path, csv_path = layer_zero_raw_paths(
        output_category="circuits",
        rendered_json_path="circuits.json",
        csv_output_path="circuits.csv",
    )

    assert json_path == Path("layers/0_layer/circuits/raw/circuits.json")
    assert csv_path == Path("layers/0_layer/circuits/raw/circuits.csv")


def test_layer_zero_raw_paths_uses_only_filename_for_nested_inputs() -> None:
    json_path, csv_path = layer_zero_raw_paths(
        output_category="seasons",
        rendered_json_path="foo/bar/seasons.json",
        csv_output_path="deep/nested/seasons.csv",
    )

    assert json_path == Path("layers/0_layer/seasons/raw/seasons.json")
    assert csv_path == Path("layers/0_layer/seasons/raw/seasons.csv")
