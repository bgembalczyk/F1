from __future__ import annotations
# ruff: noqa: I001

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scrapers.base.export.service import ExportService


def build_default_export_service() -> ExportService:
    from scrapers.base.export.exporters import DataExporter
    from scrapers.base.export.fieldnames import FieldnamesStrategySelector
    from scrapers.base.export.service import ExportService
    from scrapers.base.format.pandas_formatter import PandasDataFrameFormatter

    return ExportService(
        exporter=DataExporter(),
        fieldnames_strategy=FieldnamesStrategySelector(),
        dataframe_formatter=PandasDataFrameFormatter(),
    )
