import json
from pathlib import Path


def merge_layer_zero_raw_outputs(base_wiki_dir: Path) -> None:
    layer_zero_dir = base_wiki_dir / "layers" / "0_layer"
    if not layer_zero_dir.exists():
        return

    for domain_dir in sorted(p for p in layer_zero_dir.iterdir() if p.is_dir()):
        raw_dir = domain_dir / "raw"
        if not raw_dir.exists() or not raw_dir.is_dir():
            continue

        merged_records: list[object] = []
        for json_path in sorted(raw_dir.rglob("*.json")):
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            if isinstance(payload, list):
                merged_records.extend(payload)
            else:
                merged_records.append(payload)

        if not merged_records:
            continue

        merged_path = domain_dir / "merged.json"
        merged_path.write_text(
            json.dumps(merged_records, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
