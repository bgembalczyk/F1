# ruff: noqa: E501, PLR2004
"""Tests for PipelineRecord covering lines 16-17, 20-21, 28-29."""

import pytest

from scrapers.sponsorship_liveries.parsers.splitters.record.pipeline_record import PipelineRecord


class TestPipelineRecordPostInit:
    def test_accepts_valid_dict(self):
        record = PipelineRecord(payload={"sponsor": "Marlboro", "year": 1990})
        assert record.payload["sponsor"] == "Marlboro"

    def test_raises_type_error_for_non_dict_payload(self):
        with pytest.raises(TypeError, match="PipelineRecord payload must be a dict"):
            PipelineRecord(payload="not a dict")  # type: ignore[arg-type]

    def test_raises_type_error_for_non_str_key(self):
        with pytest.raises(TypeError, match="PipelineRecord keys must be str"):
            PipelineRecord(payload={1: "value"})  # type: ignore[arg-type]

    def test_accepts_empty_dict(self):
        record = PipelineRecord(payload={})
        assert record.payload == {}


class TestPipelineRecordFromInput:
    def test_returns_same_instance_when_already_pipeline_record(self):
        original = PipelineRecord(payload={"key": "val"})
        result = PipelineRecord.from_input(original)
        assert result is original

    def test_creates_from_mapping(self):
        result = PipelineRecord.from_input({"sponsor": "Elf", "year": 1983})
        assert isinstance(result, PipelineRecord)
        assert result.payload["sponsor"] == "Elf"

    def test_raises_type_error_for_non_mapping(self):
        with pytest.raises(TypeError, match="PipelineRecord input must be a mapping"):
            PipelineRecord.from_input("not a mapping")  # type: ignore[arg-type]

    def test_raises_type_error_for_int_input(self):
        with pytest.raises(TypeError, match="PipelineRecord input must be a mapping"):
            PipelineRecord.from_input(42)  # type: ignore[arg-type]
