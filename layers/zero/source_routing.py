from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from layers.path_resolver import PathResolver


def iter_mergeable_domain_dirs(
    layer_zero_dir: Path,
    resolver: PathResolver,
    *,
    excluded_domains: set[str] | None = None,
) -> list[Path]:
    domains_to_skip = excluded_domains or {"points", "rules"}
    domain_dirs: list[Path] = []
    for domain_dir in sorted(p for p in layer_zero_dir.iterdir() if p.is_dir()):
        raw_dir = resolver.raw_dir(domain=domain_dir.name)
        if not raw_dir.exists() or not raw_dir.is_dir():
            continue
        if domain_dir.name in domains_to_skip:
            continue
        domain_dirs.append(domain_dir)
    return domain_dirs


def load_domain_records(
    domain_dir: Path,
    resolver: PathResolver,
    *,
    transform_records: Callable[[str, str, object], list[object]],
) -> list[object]:
    merged_records: list[object] = []
    raw_dir = resolver.raw_dir(domain=domain_dir.name)
    for json_path in sorted(raw_dir.rglob("*.json")):
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        merged_records.extend(
            transform_records(domain_dir.name, json_path.name, payload),
        )
    return merged_records


def write_merged_domain_records(
    domain_dir: Path,
    merged_records: list[object],
    resolver: PathResolver,
) -> None:
    merged_path = resolver.merged(domain=domain_dir.name)
    merged_path.parent.mkdir(parents=True, exist_ok=True)
    merged_path.write_text(
        json.dumps(merged_records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
