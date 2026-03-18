from __future__ import annotations

from dataclasses import dataclass


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
        default_output_path: str,
        legacy_output_path: str,
        seed_name: str | None = None,
        output_category: str | None = None,
    ) -> ComponentMetadata:
        return cls.build(
            domain=domain,
            seed_name=seed_name,
            layer="layer_one",
            output_category=output_category,
            component_type="list_scraper",
            default_output_path=default_output_path,
            legacy_output_path=legacy_output_path,
        )
