from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scrapers.base.exporters.service import ExportService


def build_default_export_service() -> ExportService:
    from scrapers.base.exporters.data import DataExporter
    from scrapers.base.exporters.fieldnames_strategy_selector import FieldnamesStrategySelector
    from scrapers.base.exporters.service import ExportService
    from scrapers.base.formatters.pandas import PandasDataFrameFormatter

    return ExportService(
        exporter=DataExporter(),
        fieldnames_strategy=FieldnamesStrategySelector(),
        dataframe_formatter=PandasDataFrameFormatter(),
    )
