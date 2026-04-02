from __future__ import annotations

import logging
from pathlib import Path

from layers.path_resolver import PathResolver
from layers.zero.io import iter_mergeable_domain_dirs
from layers.zero.io import load_domain_payloads
from layers.zero.io import write_merged_domain_records
from layers.zero.postprocess import execute_domain_steps
from layers.zero.routing import DomainPipelineConfig
from layers.zero.routing import build_domain_pipeline_configs
from layers.zero.routing import resolve_record_transform_handlers
from scrapers.wiki.sources_registry import validate_sources_registry_consistency

logger = logging.getLogger(__name__)

DOMAIN_PIPELINE_CONFIGS: dict[str, DomainPipelineConfig] = build_domain_pipeline_configs()

validate_sources_registry_consistency()


def _transform_record(
    domain: str,
    source_name: str,
    record: object,
) -> object:
    if not isinstance(record, dict):
        return record

    transformed = dict(record)
    handlers = resolve_record_transform_handlers(
        DOMAIN_PIPELINE_CONFIGS,
        domain,
        source_name,
    )
    for handler in handlers:
        transformed = handler(domain, source_name, transformed)
    return transformed


def _iter_transformed_records(
    domain: str,
    source_name: str,
    payload: object,
) -> list[object]:
    domain_config = DOMAIN_PIPELINE_CONFIGS.get(domain, DomainPipelineConfig())

    if isinstance(payload, list):
        transformed = [_transform_record(domain, source_name, item) for item in payload]
        if domain_config.records_normalizer is None:
            return transformed
        return domain_config.records_normalizer(transformed)

    transformed_record = _transform_record(domain, source_name, payload)
    records = [transformed_record]
    if domain_config.records_normalizer is None:
        return records
    return domain_config.records_normalizer(records)


def _post_process_domain_records(domain: str, records: list[object]) -> list[object]:
    postprocessors = DOMAIN_PIPELINE_CONFIGS.get(domain, DomainPipelineConfig()).postprocessors
    return execute_domain_steps(
        domain=domain,
        step_group="postprocess",
        records=records,
        steps=postprocessors,
        logger=logger,
    )


def merge_layer_zero_raw_outputs(base_wiki_dir: Path) -> None:
    layer_zero_dir = base_wiki_dir / "layers" / "0_layer"
    if not layer_zero_dir.exists():
        return

    resolver = PathResolver(layer_zero_root=layer_zero_dir)

    for domain_dir in iter_mergeable_domain_dirs(layer_zero_dir, resolver):
        merged_records: list[object] = []
        for source_name, payload in load_domain_payloads(domain_dir, resolver):
            merged_records.extend(
                _iter_transformed_records(domain_dir.name, source_name, payload),
            )
        if not merged_records:
            continue
        merged_records = _post_process_domain_records(domain_dir.name, merged_records)
        write_merged_domain_records(domain_dir, merged_records, resolver)
