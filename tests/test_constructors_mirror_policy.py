from pathlib import Path

from layers.constructors_mirror_service import ConstructorsMirrorService
from layers.mirror_target_policy import MirrorTargetPolicy


def test_mirror_target_policy_returns_targets_by_source_category_and_year() -> None:
    policy = MirrorTargetPolicy(
        target_templates_by_source_category={
            "constructors": (
                ("chassis_constructors", "f1_constructors_{year}.json"),
                ("teams", "f1_constructors_{year}.json"),
            ),
            "drivers": (("drivers", "f1_drivers_{year}.json"),),
        },
    )

    assert policy.targets_for(source_category="constructors", year=2026) == (
        Path("layers/0_layer/chassis_constructors/raw/f1_constructors_2026.json"),
        Path("layers/0_layer/teams/raw/f1_constructors_2026.json"),
    )
    assert policy.targets_for(source_category="drivers", year=2025) == (
        Path("layers/0_layer/drivers/raw/f1_drivers_2025.json"),
    )
    assert policy.targets_for(source_category="engines", year=2026) == ()


def test_constructors_mirror_service_copies_only_targets_from_policy(tmp_path: Path) -> None:
    base_wiki_dir = tmp_path / "data" / "wiki"
    source_json_path = (
        base_wiki_dir / "layers" / "0_layer" / "constructors" / "raw" / "f1_constructors_2026.json"
    )
    source_json_path.parent.mkdir(parents=True, exist_ok=True)
    source_json_path.write_text("{}", encoding="utf-8")

    copied_targets: list[Path] = []

    mirror_service = ConstructorsMirrorService(
        mirror_target_policy=MirrorTargetPolicy(
            target_templates_by_source_category={
                "constructors": (
                    ("constructors", "f1_constructors_{year}.json"),
                    ("teams", "f1_constructors_{year}.json"),
                ),
            },
        ),
        copy_file=lambda source, target: copied_targets.append(target),
        year_provider=lambda: 2026,
    )

    mirror_service.mirror(base_wiki_dir, source_json_path)

    assert copied_targets == [
        base_wiki_dir / "layers" / "0_layer" / "teams" / "raw" / "f1_constructors_2026.json",
    ]
