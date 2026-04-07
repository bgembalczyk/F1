# ruff: noqa: E501, PLR2004
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from layers.zero.policies import CompositeLayerZeroJobHook
from layers.zero.policies import MirrorConstructorsJobHook
from layers.zero.policies import MirrorToDomainByFilenameJobHook
from layers.zero.policies import NullLayerZeroJobHook


def _make_job(name: str = "test_job") -> MagicMock:
    job = MagicMock()
    job.seed_name = name
    return job


# NullLayerZeroJobHook - line 37
def test_null_hook_after_job_runs_without_error() -> None:
    hook = NullLayerZeroJobHook()
    hook.after_job(
        base_wiki_dir=Path("/wiki"),
        job=_make_job(),
        l0_raw_json_path=Path("some/path.json"),
    )


# CompositeLayerZeroJobHook - lines 55-56
def test_composite_hook_calls_each_child_hook() -> None:
    child1 = MagicMock()
    child2 = MagicMock()
    composite = CompositeLayerZeroJobHook(hooks=(child1, child2))
    job = _make_job()
    base = Path("/wiki")
    raw = Path("raw.json")

    composite.after_job(base_wiki_dir=base, job=job, l0_raw_json_path=raw)

    child1.after_job.assert_called_once_with(
        base_wiki_dir=base,
        job=job,
        l0_raw_json_path=raw,
    )
    child2.after_job.assert_called_once_with(
        base_wiki_dir=base,
        job=job,
        l0_raw_json_path=raw,
    )


def test_composite_hook_exposes_hooks_property() -> None:
    child = MagicMock()
    composite = CompositeLayerZeroJobHook(hooks=(child,))
    assert composite.hooks == (child,)


# MirrorConstructorsJobHook - lines 73-74 (ValueError)
def test_mirror_constructors_hook_raises_when_no_mirror_service() -> None:
    with pytest.raises(ValueError, match="requires `mirror` service"):
        MirrorConstructorsJobHook(should_mirror_predicate=lambda _job: True)


def test_mirror_constructors_hook_skips_when_predicate_false() -> None:
    mirror = MagicMock()
    hook = MirrorConstructorsJobHook(
        mirror=mirror,
        should_mirror_predicate=lambda _job: False,
    )
    hook.after_job(
        base_wiki_dir=Path("/wiki"),
        job=_make_job(),
        l0_raw_json_path=Path("raw.json"),
    )
    mirror.mirror.assert_not_called()


def test_mirror_constructors_hook_calls_mirror_when_predicate_true() -> None:
    mirror = MagicMock()
    hook = MirrorConstructorsJobHook(
        mirror=mirror,
        should_mirror_predicate=lambda _job: True,
    )
    hook.after_job(
        base_wiki_dir=Path("/wiki"),
        job=_make_job(),
        l0_raw_json_path=Path("raw.json"),
    )
    mirror.mirror.assert_called_once_with(Path("/wiki"), Path("/wiki/raw.json"))


# MirrorToDomainByFilenameJobHook - lines 108-120
def test_mirror_to_domain_skips_when_predicate_false(tmp_path: Path) -> None:
    hook = MirrorToDomainByFilenameJobHook(
        target_domain="constructors",
        should_mirror_predicate=lambda _job: False,
    )
    hook.after_job(
        base_wiki_dir=tmp_path,
        job=_make_job(),
        l0_raw_json_path=Path("drivers/data.json"),
    )
    # No file should be copied - nothing to assert except no error


def test_mirror_to_domain_copies_file_to_target_domain(tmp_path: Path) -> None:
    # Create source file
    source_dir = tmp_path / "layers" / "0_layer" / "drivers" / "A_scrape"
    source_dir.mkdir(parents=True)
    source_file = source_dir / "data.json"
    source_file.write_text('{"key": "value"}')

    hook = MirrorToDomainByFilenameJobHook(
        target_domain="constructors",
        should_mirror_predicate=lambda _job: True,
    )
    hook.after_job(
        base_wiki_dir=tmp_path,
        job=_make_job(),
        l0_raw_json_path=Path("layers/0_layer/drivers/A_scrape/data.json"),
    )

    target = tmp_path / "layers" / "0_layer" / "constructors" / "A_scrape" / "data.json"
    assert target.exists()
    assert target.read_text() == '{"key": "value"}'


def test_mirror_to_domain_skips_copy_when_source_equals_target(tmp_path: Path) -> None:
    # target_domain matches the source path so target == source
    source_dir = tmp_path / "layers" / "0_layer" / "drivers" / "A_scrape"
    source_dir.mkdir(parents=True)
    source_file = source_dir / "data.json"
    source_file.write_text("{}")

    hook = MirrorToDomainByFilenameJobHook(
        target_domain="drivers",
        should_mirror_predicate=lambda _job: True,
    )
    # Should not raise even when target == source
    hook.after_job(
        base_wiki_dir=tmp_path,
        job=_make_job(),
        l0_raw_json_path=Path("layers/0_layer/drivers/A_scrape/data.json"),
    )
