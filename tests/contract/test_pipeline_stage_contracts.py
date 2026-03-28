from __future__ import annotations

from typing import Any

import logging
import pytest
from scrapers.base.pipeline_contracts import PipelineContractError
from scrapers.base.pipeline_contracts import ensure_fetch_output
from scrapers.base.pipeline_runner import ScraperPipelineRunner
from scrapers.wiki.parsers.elements.article_table_model import ensure_article_table_model


def _build_pipeline_runner(**overrides: Any) -> ScraperPipelineRunner:
    defaults = {
        "logger": logging.getLogger("pipeline-contract-test"),
        "write_step_quality_report": lambda *_args, **_kwargs: None,
        "parse_records": lambda _soup: [{"name": "Max"}],
        "normalize_records": lambda rows: rows,
        "transform_records": lambda rows: rows,
        "validate_records": lambda rows: rows,
        "post_process_records": lambda rows: rows,
    }
    defaults.update(overrides)
    return ScraperPipelineRunner(**defaults)


def test_fetch_stage_contract_requires_string_html() -> None:
    with pytest.raises(PipelineContractError, match="fetch"):
        ensure_fetch_output(b"<html></html>")


def test_parse_stage_contract_requires_record_list() -> None:
    runner = _build_pipeline_runner(parse_records=lambda _soup: {"bad": True})

    with pytest.raises(PipelineContractError, match="parse"):
        runner.run(run_id="run", html="<html></html>")


def test_normalize_stage_contract_requires_serializable_records() -> None:
    runner = _build_pipeline_runner(normalize_records=lambda _rows: [object()])

    with pytest.raises(PipelineContractError, match="normalize"):
        runner.run(run_id="run", html="<html></html>")


def test_transform_stage_contract_requires_record_list() -> None:
    runner = _build_pipeline_runner(transform_records=lambda _rows: "bad")

    with pytest.raises(PipelineContractError, match="transform"):
        runner.run(run_id="run", html="<html></html>")


def test_postprocess_stage_contract_requires_record_list() -> None:
    runner = _build_pipeline_runner(post_process_records=lambda _rows: "bad")

    with pytest.raises(PipelineContractError, match="postprocess"):
        runner.run(run_id="run", html="<html></html>")


def test_article_table_model_contract_requires_explicit_keys() -> None:
    with pytest.raises(ValueError, match="missing key 'rows'"):
        ensure_article_table_model({"headers": ["Year"]})
