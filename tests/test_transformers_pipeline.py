from dataclasses import dataclass
import logging
from pathlib import Path
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from scrapers.base.transformers import RecordTransformer
from scrapers.base.transformers import RecordFactoryTransformer, TransformersPipeline
from validation.records import ExportRecord


def test_transformers_pipeline_applies_in_order_and_logs(
    caplog: pytest.LogCaptureFixture,
) -> None:
    class AddFlagTransformer(RecordTransformer):
        def transform(self, records: list[ExportRecord]) -> list[ExportRecord]:
            for record in records:
                record["flag"] = True
            return records

    class AddLabelTransformer(RecordTransformer):
        def transform(self, records: list[ExportRecord]) -> list[ExportRecord]:
            for record in records:
                record["label"] = "flagged" if record.get("flag") else "plain"
            return records

    pipeline = TransformersPipeline([AddFlagTransformer(), AddLabelTransformer()])

    with caplog.at_level(logging.DEBUG):
        records = pipeline.apply([{"name": "Max"}])

    assert records == [{"name": "Max", "flag": True, "label": "flagged"}]
    assert "Transformer AddFlagTransformer: before=1" in caplog.text
    assert "Transformer AddLabelTransformer: after=1" in caplog.text


def test_record_factory_transformer_applies_factory() -> None:
    @dataclass
    class DriverRecord:
        name: str

    transformer = RecordFactoryTransformer(DriverRecord)

    records = transformer.transform([{"name": "Lewis"}])

    assert records == [DriverRecord(name="Lewis")]
