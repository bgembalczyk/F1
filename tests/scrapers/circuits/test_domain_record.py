# ruff: noqa: E501, PLR2004
from unittest.mock import MagicMock

import pytest

from scrapers.circuits.circuits_services.domain_record import CircuitDomainRecordInput
from scrapers.circuits.circuits_services.domain_record import DomainRecordService


@pytest.fixture()
def service() -> DomainRecordService:
    return DomainRecordService()


def _payload(**overrides):
    base = {
        "source_url": "https://en.wikipedia.org/wiki/Monza",
        "soup": MagicMock(),
        "infobox": {},
        "sections": [],
        "include_urls": False,
        "fetcher": None,
        "policy": None,
        "debug_dir": None,
    }
    base.update(overrides)
    return CircuitDomainRecordInput(**base)


def test_execute_with_no_tables_returns_empty_lap_records() -> None:
    mock_parser = MagicMock()
    mock_parser.parse.return_value = []
    mock_assembler = MagicMock()
    mock_assembler.assemble.return_value = {"url": "https://example.com", "name": "Test"}

    svc = DomainRecordService(assembler=mock_assembler, article_tables_parser=mock_parser)
    result = svc.execute(_payload(source_url="https://example.com"))

    assert result.record == {"url": "https://example.com", "name": "Test"}
    assembled_dto = mock_assembler.assemble.call_args[0][0]
    assert assembled_dto.lap_record_rows == []


def test_execute_table_without_table_key_is_skipped() -> None:
    mock_parser = MagicMock()
    mock_parser.parse.return_value = [{"headers": [], "table_type": None}]
    mock_assembler = MagicMock()
    mock_assembler.assemble.return_value = {"url": "https://example.com"}

    svc = DomainRecordService(assembler=mock_assembler, article_tables_parser=mock_parser)
    result = svc.execute(_payload(source_url="https://example.com"))

    assert result.record == {"url": "https://example.com"}
    assembled_dto = mock_assembler.assemble.call_args[0][0]
    assert assembled_dto.lap_record_rows == []


def test_execute_returns_domain_record() -> None:
    mock_assembler = MagicMock()
    mock_assembler.assemble.return_value = {
        "url": "https://example.com",
        "name": "Test",
    }
    svc = DomainRecordService(assembler=mock_assembler)

    result = svc.execute(_payload(source_url="https://example.com"))

    assert result.record == {"url": "https://example.com", "name": "Test"}
    mock_assembler.assemble.assert_called_once()
