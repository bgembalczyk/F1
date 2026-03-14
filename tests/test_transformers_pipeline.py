import logging
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

from scrapers.base.helpers.transformers import build_transformers
from scrapers.base.transformers.normalize_links import NormalizeLinksTransformer
from scrapers.base.transformers.pipeline import TransformersPipeline
from scrapers.base.transformers.record_factory import RecordFactoryTransformer
from scrapers.base.transformers.record_transformer import RecordTransformer
from validation.validator_base import ExportRecord

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))


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


def test_build_transformers_adds_default_normalizer() -> None:
    transformers = build_transformers([])

    assert any(
        isinstance(transformer, NormalizeLinksTransformer)
        for transformer in transformers
    )


def test_normalize_links_transformer_normalizes_link_values() -> None:
    transformer = NormalizeLinksTransformer()

    records = transformer.transform(
        [
            {
                "driver": {"text": " Lewis ", "url": "https://example.com/lewis"},
                "seasons": [2020, 2021],
            },
        ],
    )

    assert records == [
        {
            "driver": {"text": "Lewis", "url": "https://example.com/lewis"},
            "seasons": [2020, 2021],
        },
    ]
