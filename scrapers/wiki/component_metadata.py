from __future__ import annotations

from dataclasses import dataclass
from typing import Any

LIST_SCRAPER_KIND = "list_scraper"
COMPLETE_SCRAPER_KIND = "complete_scraper"
RUNNER_KIND = "runner"


@dataclass(frozen=True)
class ComponentMetadata:
    domain: str
    seed_name: str
    layer: str
    output_category: str
    component_type: str
    default_output_path: str | None = None
    legacy_output_path: str | None = None

    @classmethod
    def build(
        cls,
        *,
        domain: str,
        seed_name: str | None = None,
        layer: str,
        output_category: str | None = None,
        component_type: str,
        default_output_path: str | None = None,
        legacy_output_path: str | None = None,
    ) -> ComponentMetadata:
        normalized_seed_name = seed_name or domain
        normalized_output_category = output_category or domain
        return cls(
            domain=domain,
            seed_name=normalized_seed_name,
            layer=layer,
            output_category=normalized_output_category,
            component_type=component_type,
            default_output_path=default_output_path,
            legacy_output_path=legacy_output_path,
        )

    @classmethod
    def build_layer_one_list_scraper(
        cls,
        *,
        domain: str,
        default_output_path: str | None = None,
        legacy_output_path: str | None = None,
        seed_name: str | None = None,
        output_category: str | None = None,
    ) -> ComponentMetadata:
        return build_component_metadata(
            domain=domain,
            kind=LIST_SCRAPER_KIND,
            seed_name=seed_name,
            output_category=output_category,
            default_output_path=default_output_path,
            legacy_output_path=legacy_output_path,
        )


def _default_output_stem(domain: str, kind: str) -> str:
    if kind == LIST_SCRAPER_KIND:
        return f"complete_{domain}"
    if kind == COMPLETE_SCRAPER_KIND:
        return f"complete_{domain}"
    return domain


def _default_output_paths(
    *,
    domain: str,
    kind: str,
    default_output_path: str | None,
    legacy_output_path: str | None,
) -> tuple[str | None, str | None]:
    if default_output_path is not None and legacy_output_path is not None:
        return default_output_path, legacy_output_path

    if kind not in {LIST_SCRAPER_KIND, COMPLETE_SCRAPER_KIND}:
        return default_output_path, legacy_output_path

    stem = _default_output_stem(domain, kind)
    segment = "seeds" if kind == LIST_SCRAPER_KIND else "complete"

    resolved_default = default_output_path or f"raw/{domain}/{segment}/{stem}"
    resolved_legacy = legacy_output_path or f"{domain}/{stem}"
    return resolved_default, resolved_legacy


def build_component_metadata(
    *,
    domain: str,
    kind: str,
    default_output_path: str | None = None,
    legacy_output_path: str | None = None,
    seed_name: str | None = None,
    output_category: str | None = None,
) -> ComponentMetadata:
    layer = "layer_one" if kind in {LIST_SCRAPER_KIND, RUNNER_KIND} else "layer_two"
    resolved_default, resolved_legacy = _default_output_paths(
        domain=domain,
        kind=kind,
        default_output_path=default_output_path,
        legacy_output_path=legacy_output_path,
    )
    metadata = ComponentMetadata.build(
        domain=domain,
        seed_name=seed_name,
        layer=layer,
        output_category=output_category,
        component_type=kind,
        default_output_path=resolved_default,
        legacy_output_path=resolved_legacy,
    )
    validate_component_metadata(metadata)
    return metadata


def parse_component_metadata(raw: Any) -> ComponentMetadata:
    if isinstance(raw, ComponentMetadata):
        metadata = raw
    elif isinstance(raw, dict):
        metadata = ComponentMetadata(**raw)
    else:
        msg = f"Unsupported metadata format: {type(raw)!r}"
        raise TypeError(msg)
    validate_component_metadata(metadata)
    return metadata


def validate_component_metadata(metadata: ComponentMetadata) -> None:
    if not metadata.domain:
        raise ValueError("metadata.domain cannot be empty")
    if not metadata.component_type:
        raise ValueError("metadata.component_type cannot be empty")
    if not metadata.layer:
        raise ValueError("metadata.layer cannot be empty")
    if metadata.component_type in {LIST_SCRAPER_KIND, COMPLETE_SCRAPER_KIND}:
        if not metadata.default_output_path or not metadata.legacy_output_path:
            msg = (
                "metadata.default_output_path and metadata.legacy_output_path "
                "are required for list/complete scrapers"
            )
            raise ValueError(msg)
        if not metadata.default_output_path.startswith(f"raw/{metadata.domain}/"):
            msg = (
                "metadata.default_output_path must use raw/<domain>/... convention, "
                f"got: {metadata.default_output_path!r}"
            )
            raise ValueError(msg)
        if not metadata.legacy_output_path.startswith(f"{metadata.domain}/"):
            msg = (
                "metadata.legacy_output_path must use <domain>/... convention, "
                f"got: {metadata.legacy_output_path!r}"
            )
            raise ValueError(msg)


def validate_metadata_for_component_class(component_cls: type[Any]) -> None:
    raw = getattr(component_cls, "COMPONENT_METADATA", None)
    if raw is None:
        return
    metadata = parse_component_metadata(raw)
    component_cls.COMPONENT_METADATA = metadata
