from __future__ import annotations

from collections.abc import Iterable
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING
from warnings import warn

from scrapers.columns.base import BaseColumn
from scrapers.columns.spec import ColumnSpec
from scrapers.config_table import TableScraperConfig
from scrapers.constants_table import BASE_STATS_COLUMNS
from scrapers.constants_table import BASE_STATS_MAP
from scrapers.schema_table import TableSchema
from scrapers.schema_table import TableSchemaBuilder
from scrapers.table_schema_dsl import TableSchemaDSL


@dataclass(frozen=True)
class MetricColumnSpec:
    header: str
    output_key: str
    metric_key: str


@dataclass(frozen=True)
class EntityColumnSpec:
    header: str
    output_key: str
    column_type: BaseColumn


SchemaPart = ColumnSpec | Sequence[ColumnSpec]


def build_columns(*parts: SchemaPart) -> list[ColumnSpec]:
    columns: list[ColumnSpec] = []
    for part in parts:
        if isinstance(part, ColumnSpec):
            columns.append(part)
            continue
        columns.extend(part)
    return columns


def build_entity_metadata_columns(
    specs: Sequence[EntityColumnSpec],
) -> list[ColumnSpec]:
    return [
        ColumnSpec(spec.header, spec.output_key, spec.column_type) for spec in specs
    ]


def build_metric_columns(
    specs: Sequence[MetricColumnSpec],
    *,
    column_overrides: dict[str, BaseColumn] | None = None,
) -> list[ColumnSpec]:

    column_overrides = column_overrides or {}
    return [
        ColumnSpec(
            spec.header,
            spec.output_key,
            column_overrides.get(spec.metric_key, BASE_STATS_COLUMNS[spec.metric_key]),
        )
        for spec in specs
    ]


def build_base_stats_columns(
    *,
    key_aliases: dict[str, str] | None = None,
    column_overrides: dict[str, BaseColumn] | None = None,
    include: Iterable[str] | None = None,
    exclude: Iterable[str] | None = None,
) -> list[ColumnSpec]:

    include_set = set(include) if include is not None else None
    exclude_set = set(exclude or [])
    key_aliases = key_aliases or {}

    specs = [
        MetricColumnSpec(
            header,
            key_aliases.get(metric_key, metric_key),
            metric_key,
        )
        for header, metric_key in BASE_STATS_MAP.items()
        if (include_set is None or metric_key in include_set)
        and metric_key not in exclude_set
    ]
    return build_metric_columns(specs, column_overrides=column_overrides)


def build_name_status_fragment(
    *,
    header: str,
    output_key: str,
    column_type: BaseColumn,
) -> list[ColumnSpec]:
    return [ColumnSpec(header, output_key, column_type)]


