from __future__ import annotations

from exporters.data import DataExporter
from exporters.service import ExportService
from scrapers.fieldnames_strategy_selector import FieldnamesStrategySelector
from scrapers.formatters.pandas import PandasDataFrameFormatter


def build_default_export_service() -> ExportService:
    return ExportService(
        exporter=DataExporter(),
        fieldnames_strategy=FieldnamesStrategySelector(),
        dataframe_formatter=PandasDataFrameFormatter(),
    )
