from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field

from layers.zero.domain_transforms import DEFAULT_SOURCE_PIPELINE
from layers.zero.domain_transforms import RecordTransformHandler
from layers.zero.domain_transforms import build_domain_transformers
from layers.zero.domain_transforms import normalize_engine_records
from layers.zero.domain_transforms import normalize_race_records
from layers.zero.postprocess import DomainStep
from layers.zero.postprocess import build_domain_postprocess_steps


@dataclass(frozen=True)
class DomainPipelineConfig:
    transformers: dict[str, tuple[RecordTransformHandler, ...]] = field(
        default_factory=dict,
    )
    postprocessors: tuple[DomainStep, ...] = ()
    records_normalizer: Callable[[list[object]], list[object]] | None = None


def build_domain_pipeline_configs() -> dict[str, DomainPipelineConfig]:
    postprocess_steps = build_domain_postprocess_steps()
    transformer_map = build_domain_transformers()
    normalizers = {
        "engines": normalize_engine_records,
        "races": normalize_race_records,
    }

    domains = set(transformer_map) | set(postprocess_steps) | set(normalizers)
    return {
        domain: DomainPipelineConfig(
            transformers=transformer_map.get(domain, {}),
            postprocessors=postprocess_steps.get(domain, ()),
            records_normalizer=normalizers.get(domain),
        )
        for domain in domains
    }


def resolve_record_transform_handlers(
    pipeline_configs: dict[str, DomainPipelineConfig],
    domain: str,
    source_name: str,
) -> tuple[RecordTransformHandler, ...]:
    global_handlers = pipeline_configs.get("*", DomainPipelineConfig()).transformers
    domain_handlers = pipeline_configs.get(domain, DomainPipelineConfig()).transformers

    resolved: list[RecordTransformHandler] = [
        *global_handlers.get(DEFAULT_SOURCE_PIPELINE, ()),
        *global_handlers.get(source_name, ()),
    ]
    domain_pipeline = domain_handlers.get(source_name)
    if domain_pipeline is None:
        domain_pipeline = domain_handlers.get(DEFAULT_SOURCE_PIPELINE, ())
    resolved.extend(domain_pipeline)
    return tuple(resolved)
