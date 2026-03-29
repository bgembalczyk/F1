from __future__ import annotations

from scrapers.base.export.exporters import DataExporter
from scrapers.base.export.fieldnames import FieldnamesStrategySelector
from scrapers.base.export.service import ExportService
from scrapers.base.format.pandas_formatter import PandasDataFrameFormatter


def create_default_export_service() -> ExportService:
    return ExportService(
        exporter=DataExporter(),
        fieldnames_strategy=FieldnamesStrategySelector(),
        dataframe_formatter=PandasDataFrameFormatter(),
    )
