# ruff: noqa: E501, PLR2004
from typing import Any
from unittest.mock import MagicMock

import pytest

from scrapers.circuits.services.domain_record import DomainRecordService


@pytest.fixture()
def service() -> DomainRecordService:
    return DomainRecordService()


# ---------------------------------------------------------------------------
# collect_lap_record_rows  (lines 53-66)
# ---------------------------------------------------------------------------

def test_collect_lap_record_rows_no_tables(service) -> None:
    # When article_tables_parser returns empty list → empty result
    mock_parser = MagicMock()
    mock_parser.parse.return_value = []
    svc = DomainRecordService(article_tables_parser=mock_parser)
    result = svc.collect_lap_record_rows(
        soup=MagicMock(),
        url="https://en.wikipedia.org/wiki/Monza",
        include_urls=False,
        fetcher=None,
        policy=None,
        debug_dir=None,
    )
    assert result == []


def test_collect_lap_record_rows_table_without_table_key(service) -> None:
    # table_data missing "_table" key → skipped
    mock_parser = MagicMock()
    mock_parser.parse.return_value = [{"headers": [], "table_type": None}]
    svc = DomainRecordService(article_tables_parser=mock_parser)
    result = svc.collect_lap_record_rows(
        soup=MagicMock(),
        url="https://en.wikipedia.org/wiki/Monza",
        include_urls=False,
        fetcher=None,
        policy=None,
        debug_dir=None,
    )
    assert result == []


def test_collect_lap_record_rows_non_lap_table_skipped(service) -> None:
    mock_parser = MagicMock()
    mock_table = MagicMock()
    mock_parser.parse.return_value = [
        {"_table": mock_table, "headers": ["Name", "Date"], "table_type": "other"}
    ]
    svc = DomainRecordService(article_tables_parser=mock_parser)
    result = svc.collect_lap_record_rows(
        soup=MagicMock(),
        url="https://en.wikipedia.org/wiki/Monza",
        include_urls=False,
        fetcher=None,
        policy=None,
        debug_dir=None,
    )
    assert result == []


# ---------------------------------------------------------------------------
# assemble_record  (line 80)
# ---------------------------------------------------------------------------

def test_assemble_record_returns_dict(service) -> None:
    mock_assembler = MagicMock()
    mock_assembler.assemble.return_value = {"url": "https://example.com", "name": "Test"}
    svc = DomainRecordService(assembler=mock_assembler)
    result = svc.assemble_record(
        source_url="https://example.com",
        infobox={},
        lap_record_rows=[],
        sections=[],
    )
    assert result == {"url": "https://example.com", "name": "Test"}
    mock_assembler.assemble.assert_called_once()
