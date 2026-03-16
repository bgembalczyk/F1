from pathlib import Path

import pytest

from scrapers.data_paths import DataPaths
from scrapers.data_paths import DomainId


def test_data_paths_layout_matches_roadmap_and_uml(tmp_path: Path) -> None:
    paths = DataPaths(base_dir=tmp_path / "data")

    assert paths.raw_list_file("drivers", "f1_drivers.json") == (
        tmp_path / "data" / "raw" / "drivers" / "list" / "f1_drivers.json"
    )
    assert paths.raw_seed_file("drivers", "complete_drivers") == (
        tmp_path / "data" / "raw" / "drivers" / "seeds" / "complete_drivers"
    )
    assert paths.normalized_file("drivers", "f1_drivers.json") == (
        tmp_path / "data" / "normalized" / "drivers" / "f1_drivers.json"
    )
    assert paths.checkpoint_step_file(1, "layer1", "drivers") == (
        tmp_path / "data" / "checkpoints" / "step_1_layer1_drivers.json"
    )


def test_domain_id_and_checkpoint_filename_policy() -> None:
    assert str(DomainId(" Drivers ")) == "drivers"

    paths = DataPaths(base_dir=Path("data"))
    assert paths.checkpoint_filename(2, "layer0", "Grands Prix") == "step_2_layer0_grands_prix.json"


@pytest.mark.parametrize("value", ["", "drivers/wiki", "drivers\\legacy"])
def test_domain_id_rejects_invalid_values(value: str) -> None:
    with pytest.raises(ValueError):
        DomainId(value)
