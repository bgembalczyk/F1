"""Layer Zero Phase D: Merge C_extract files into D_merge output."""

from __future__ import annotations

import json
from pathlib import Path

from layers.path_resolver import PathResolver


def merge_layer_zero_phase_d(base_wiki_dir: Path) -> None:
    """Phase D: merge all C_extract files per domain into D_merge output."""
    layer_zero_dir = base_wiki_dir / "layers" / "0_layer"
    if not layer_zero_dir.exists():
        return

    resolver = PathResolver(layer_zero_root=layer_zero_dir)

    for domain_dir in sorted(p for p in layer_zero_dir.iterdir() if p.is_dir()):
        extract_dir = resolver.extract_dir(domain=domain_dir.name)
        if not extract_dir.exists() or not extract_dir.is_dir():
            continue

        json_files = sorted(extract_dir.rglob("*.json"))
        if not json_files:
            continue

        all_records: list[object] = []
        for json_path in json_files:
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            if isinstance(payload, list):
                all_records.extend(payload)
            else:
                all_records.append(payload)

        merged_records = _dedupe_records(all_records)

        d_merge_dir = resolver.d_merge_dir(domain=domain_dir.name)
        d_merge_dir.mkdir(parents=True, exist_ok=True)
        out_path = resolver.d_merged(domain=domain_dir.name)
        out_path.write_text(
            json.dumps(merged_records, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def _dedupe_records(records: list[object]) -> list[object]:
    seen: set[str] = set()
    result: list[object] = []
    for record in records:
        key = _dedup_key(record)
        if key in seen:
            continue
        seen.add(key)
        result.append(record)
    return result


def _dedup_key(record: object) -> str:
    if isinstance(record, dict):
        url = record.get("url")
        if url is not None:
            return str(url)
        text = record.get("text")
        if text is not None:
            return f"text:{text}"
        return json.dumps(record, sort_keys=True, ensure_ascii=False)
    return json.dumps(record, ensure_ascii=False)
