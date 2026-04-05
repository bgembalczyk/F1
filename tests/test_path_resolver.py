from pathlib import Path

from layers.path_resolver import DEFAULT_PATH_RESOLVER


def test_default_exports_root_points_to_data_directory() -> None:
    assert DEFAULT_PATH_RESOLVER.exports_root == Path("data")
