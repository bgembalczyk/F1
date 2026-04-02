from __future__ import annotations

from pathlib import Path

from .io import iter_mergeable_domain_dirs
from .io import load_domain_payloads
from .io import write_merged_domain_records
from .post_processors import post_process_domain_records
from .transformers.config import resolve_record_transform_handlers


def transform_payload(domain: str, source_name: str, payload: object) -> list[object]:
    if isinstance(payload, list):
        return [transform_record(domain, source_name, item) for item in payload]
    return [transform_record(domain, source_name, payload)]


def transform_record(domain: str, source_name: str, record: object) -> object:
    if not isinstance(record, dict):
        return record

    transformed = dict(record)
    for handler in resolve_record_transform_handlers(domain, source_name):
        transformed = handler(domain, source_name, transformed)
    return transformed


def merge_layer_zero_raw_outputs(base_wiki_dir: Path) -> None:
    layer_zero_dir = base_wiki_dir / "layers" / "0_layer"
    if not layer_zero_dir.exists():
        return

    for domain_dir in iter_mergeable_domain_dirs(layer_zero_dir):
        payloads = load_domain_payloads(domain_dir)
        merged_records: list[object] = []
        for domain, source_name, payload in payloads:
            merged_records.extend(transform_payload(domain, source_name, payload))
        if not merged_records:
            continue

        merged_records = post_process_domain_records(domain_dir.name, merged_records)
        write_merged_domain_records(domain_dir, merged_records)
