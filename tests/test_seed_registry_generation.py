from layers.seed.registry.constants import EXPLICIT_LAYER_ONE_SEED_REGISTRY
from layers.seed.registry.constants import RAW_REGISTRY_SPEC
from layers.seed.registry import WIKI_LIST_JOB_REGISTRY
from layers.seed.registry.constants import build_list_job_registry_entry_from_spec
from layers.seed.registry.constants import build_seed_registry_entry_from_spec


def test_generated_seed_registry_matches_legacy_contract() -> None:
    generated = tuple(
        entry
        for entry in (
            build_seed_registry_entry_from_spec(spec) for spec in RAW_REGISTRY_SPEC
        )
        if entry is not None
    )

    by_seed = {entry.seed_name: entry for entry in generated}
    assert [entry.seed_name for entry in EXPLICIT_LAYER_ONE_SEED_REGISTRY] == [
        "drivers",
        "constructors",
        "grands_prix",
        "circuits",
        "seasons",
    ]
    assert by_seed["drivers"].default_output_path == "raw/drivers/seeds/complete_drivers"
    assert by_seed["drivers"].legacy_output_path == "drivers/complete_drivers"
    assert (
        by_seed["constructors"].default_output_path
        == "raw/constructors/seeds/complete_constructors"
    )
    assert by_seed["constructors"].legacy_output_path == "constructors/complete_constructors"
    assert (
        by_seed["grands_prix"].default_output_path
        == "raw/grands_prix/seeds/f1_grands_prix_extended.json"
    )
    assert (
        by_seed["grands_prix"].legacy_output_path
        == "grands_prix/f1_grands_prix_extended.json"
    )
    assert by_seed["circuits"].default_output_path == "raw/circuits/seeds/complete_circuits"
    assert by_seed["circuits"].legacy_output_path == "circuits/complete_circuits"
    assert by_seed["seasons"].default_output_path == "raw/seasons/seeds/complete_seasons"
    assert by_seed["seasons"].legacy_output_path == "seasons/complete_seasons"


def test_generated_list_job_registry_matches_legacy_contract() -> None:
    generated = tuple(
        build_list_job_registry_entry_from_spec(spec)
        for spec in RAW_REGISTRY_SPEC
        if spec.include_in_list_registry
    )

    assert generated == WIKI_LIST_JOB_REGISTRY

    jobs_by_seed = {entry.seed_name: entry for entry in generated}
    assert jobs_by_seed["constructors_current"].json_output_path == (
        "raw/constructors/list/f1_constructors_{year}.json"
    )
    assert jobs_by_seed["constructors_current"].legacy_json_output_path == (
        "constructors/f1_constructors_{year}.json"
    )
    assert jobs_by_seed["constructors_former"].output_category == "chassis_constructors"
    assert jobs_by_seed["constructors_privateer"].output_category == "teams"
    assert jobs_by_seed["engines_regulations"].json_output_path == (
        "raw/rules/list/f1_engine_regulations.json"
    )
    assert jobs_by_seed["grands_prix_red_flagged_world_championship"].output_category == (
        "races"
    )
