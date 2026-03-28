from __future__ import annotations

from collections.abc import Iterable
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

from scrapers.base.table.dsl.column import ColumnSpec
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL

if TYPE_CHECKING:
    from scrapers.base.table.columns.types.base import BaseColumn
    from scrapers.base.table.config import ScraperConfig
    from scrapers.base.table.schema import TableSchema
    from scrapers.base.table.schema import TableSchemaBuilder


@dataclass(frozen=True)
class MetricColumnSpec:
    header: str
    key: str
    metric_key: str


def metric_column(header: str, key: str, metric_key: str) -> MetricColumnSpec:
    return MetricColumnSpec(header=header, key=key, metric_key=metric_key)


SchemaPart = ColumnSpec | Sequence[ColumnSpec]


def build_columns(*parts: SchemaPart) -> list[ColumnSpec]:
    columns: list[ColumnSpec] = []
    for part in parts:
        if isinstance(part, ColumnSpec):
            columns.append(part)
            continue
        columns.extend(part)
    return columns


def build_metric_columns(
    specs: Sequence[MetricColumnSpec],
    *,
    column_overrides: dict[str, BaseColumn] | None = None,
) -> list[ColumnSpec]:
    from scrapers.base.table.constants import BASE_STATS_COLUMNS

    column_overrides = column_overrides or {}
    return [
        column(
            spec.header,
            spec.key,
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
    from scrapers.base.table.constants import BASE_STATS_MAP

    include_set = set(include) if include is not None else None
    exclude_set = set(exclude or [])
    key_aliases = key_aliases or {}

    specs = [
        metric_column(
            header,
            key_aliases.get(metric_key, metric_key),
            metric_key,
        )
        for header, metric_key in BASE_STATS_MAP.items()
        if (include_set is None or metric_key in include_set)
        and metric_key not in exclude_set
    ]
    return build_metric_columns(specs, column_overrides=column_overrides)


def build_table_schema(*parts: SchemaPart) -> TableSchemaDSL:
    return TableSchemaDSL(columns=build_columns(*parts))


def build_scraper_config(
    *,
    url: str,
    columns: Sequence[ColumnSpec] | None = None,
    schema: TableSchema | TableSchemaBuilder | TableSchemaDSL | None = None,
    section_id: str | None = None,
    expected_headers: Sequence[str] | None = None,
    table_css_class: str = "wikitable",
    record_factory=None,
    model_class: type | None = None,
) -> ScraperConfig:
    from scrapers.base.table.config import ScraperConfig

    if columns is None and schema is None:
        msg = "Either columns or schema must be provided."
        raise ValueError(msg)

    if columns is not None and schema is not None:
        msg = "Provide only one of columns or schema."
        raise ValueError(msg)

    resolved_schema = build_table_schema(columns) if columns is not None else schema

    return ScraperConfig(
        url=url,
        section_id=section_id,
        expected_headers=expected_headers,
        record_factory=record_factory,
        model_class=model_class,
        table_css_class=table_css_class,
        schema=resolved_schema,
    )
