import json
from pathlib import Path

import pytest

from scrapers.base.orchestration.components.source_path_resolver import SourcePathResolver
from scrapers.base.orchestration.models import OrchestrationPaths
from scrapers.base.orchestration.models import StepDeclaration


def _step() -> StepDeclaration:
    return StepDeclaration(
        step_id=1,
        layer="layer1",
        input_source="drivers",
        parser=lambda rows: rows,
        output_target="checkpoints",
    )


def test_source_path_resolver_prefers_default_checkpoint_raw_legacy_order(
    tmp_path: Path,
) -> None:
    checkpoints_path = tmp_path / "data" / "checkpoints" / "drivers.json"
    raw_path = tmp_path / "data" / "raw" / "drivers" / "drivers.json"
    legacy_path = tmp_path / "data" / "wiki" / "drivers" / "drivers.json"

    for path in (checkpoints_path, raw_path, legacy_path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps([{"url": str(path)}]), encoding="utf-8")

    resolver = SourcePathResolver(paths=OrchestrationPaths(base_dir=tmp_path / "data"))

    resolved = resolver.resolve(_step(), "drivers")

    assert resolved == checkpoints_path


def test_source_path_resolver_allows_custom_fallback_order(tmp_path: Path) -> None:
    raw_path = tmp_path / "data" / "raw" / "drivers" / "drivers.json"
    legacy_path = tmp_path / "data" / "wiki" / "drivers" / "drivers.json"

    raw_path.parent.mkdir(parents=True, exist_ok=True)
    legacy_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(json.dumps([{"url": "raw"}]), encoding="utf-8")
    legacy_path.write_text(json.dumps([{"url": "legacy"}]), encoding="utf-8")

    resolver = SourcePathResolver(
        paths=OrchestrationPaths(base_dir=tmp_path / "data"),
        fallback_order=("legacy", "raw", "checkpoint"),
    )

    resolved = resolver.resolve(_step(), "drivers")

    assert resolved == legacy_path


def test_source_path_resolver_raises_for_unsupported_resolver_name(
    tmp_path: Path,
) -> None:
    resolver = SourcePathResolver(
        paths=OrchestrationPaths(base_dir=tmp_path / "data"),
        fallback_order=("invalid",),
    )

    with pytest.raises(ValueError, match="Unsupported source resolver"):
        resolver.resolve(_step(), "drivers")
