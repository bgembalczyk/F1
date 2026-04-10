# ruff: noqa: E501, PLR2004
from unittest.mock import MagicMock

from scrapers.services.domain_record.circuit import CircuitDomainRecordInput
from scrapers.services.domain_record.circuit import DomainRecordService
from scrapers.services.domain_record.circuit_lap_records_extraction_service import (
    CircuitLapRecordsExtractionService,
)


def test_collect_lap_record_rows_no_tables() -> None:
    mock_parser = MagicMock()
    mock_parser.parse.return_value = []
    svc = CircuitLapRecordsExtractionService(article_tables_parser=mock_parser)
    result = svc.collect_lap_record_rows(
        soup=MagicMock(),
        url="https://en.wikipedia.org/wiki/Monza",
        include_urls=False,
        fetcher=None,
        policy=None,
        debug_dir=None,
    )
    assert result == []


def test_collect_lap_record_rows_table_without_table_key() -> None:
    mock_parser = MagicMock()
    mock_parser.parse.return_value = [{"headers": [], "table_type": None}]
    svc = CircuitLapRecordsExtractionService(article_tables_parser=mock_parser)
    result = svc.collect_lap_record_rows(
        soup=MagicMock(),
        url="https://en.wikipedia.org/wiki/Monza",
        include_urls=False,
        fetcher=None,
        policy=None,
        debug_dir=None,
    )
    assert result == []


def test_collect_lap_record_rows_non_lap_table_skipped() -> None:
    mock_parser = MagicMock()
    mock_table = MagicMock()
    mock_parser.parse.return_value = [
        {"_table": mock_table, "headers": ["Name", "Date"], "table_type": "other"},
    ]
    svc = CircuitLapRecordsExtractionService(article_tables_parser=mock_parser)
    result = svc.collect_lap_record_rows(
        soup=MagicMock(),
        url="https://en.wikipedia.org/wiki/Monza",
        include_urls=False,
        fetcher=None,
        policy=None,
        debug_dir=None,
    )
    assert result == []


def test_assemble_record_returns_dict() -> None:
    mock_assembler = MagicMock()
    mock_assembler.assemble.return_value = {
        "url": "https://example.com",
        "name": "Test",
    }
    svc = DomainRecordService(assembler=mock_assembler)
    result = svc.assemble_record(
        CircuitDomainRecordInput(
            source_url="https://example.com",
            infobox={},
            lap_record_rows=[],
            sections=[],
        ),
    )
    assert result == {"url": "https://example.com", "name": "Test"}
    mock_assembler.assemble.assert_called_once()
