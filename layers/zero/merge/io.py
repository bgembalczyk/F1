from __future__ import annotations

import json
from pathlib import Path


DomainPayload = tuple[str, str, object]


def iter_mergeable_domain_dirs(layer_zero_dir: Path) -> list[Path]:
    domain_dirs: list[Path] = []
    for domain_dir in sorted(p for p in layer_zero_dir.iterdir() if p.is_dir()):
        raw_dir = domain_dir / "raw"
        if not raw_dir.exists() or not raw_dir.is_dir():
            continue
        if domain_dir.name in {"points", "rules"}:
            continue
        domain_dirs.append(domain_dir)
    return domain_dirs


def load_domain_payloads(domain_dir: Path) -> list[DomainPayload]:
    payloads: list[DomainPayload] = []
    raw_dir = domain_dir / "raw"
    for json_path in sorted(raw_dir.rglob("*.json")):
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        payloads.append((domain_dir.name, json_path.name, payload))
    return payloads


def write_merged_domain_records(domain_dir: Path, merged_records: list[object]) -> None:
    merged_path = domain_dir / f"{domain_dir.name}.json"
    merged_path.write_text(
        json.dumps(merged_records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
