from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest

from scrapers.constructors.constructors_postprocess.assembler import ConstructorRecordDTO
from scrapers.drivers.drivers_postprocess.assembler import DriverRecordDTO
from scrapers.records.dto.circuit import CircuitRecordDTO
from scrapers.seasons.postprocess_seasons.assembler import SeasonPayloadDTO
from scrapers.seasons.postprocess_seasons.assembler import SeasonRecordSections
from scrapers.services.domain_record.base_pipeline_service import BaseDomainPipelineService
from scrapers.services.domain_record.circuit_pipeline_service import CircuitDomainRecordInput
from scrapers.services.domain_record.circuit_pipeline_service import CircuitPipelineService
from scrapers.services.domain_record.constructor_pipeline_service import (
    ConstructorDomainRecordInput,
)
from scrapers.services.domain_record.constructor_pipeline_service import (
    ConstructorPipelineService,
)
from scrapers.services.domain_record.driver_pipeline_service import DriverDomainRecordInput
from scrapers.services.domain_record.driver_pipeline_service import DriverPipelineService
from scrapers.services.domain_record.season_pipeline_service import SeasonDomainRecordInput
from scrapers.services.domain_record.season_pipeline_service import SeasonPipelineService


@dataclass(frozen=True)
class DomainCase:
    service: type[BaseDomainPipelineService]
    input_dto: object
    source: dict[str, object]


@pytest.fixture(
    params=[
        DomainCase(
            service=DriverPipelineService,
            input_dto=DriverDomainRecordInput(url="u", infobox={}, career_results=[]),
            source={"url": "u", "infobox": {}, "career_results": []},
        ),
        DomainCase(
            service=ConstructorPipelineService,
            input_dto=ConstructorDomainRecordInput(
                url="u",
                infoboxes=[],
                tables=[],
                sections=[],
            ),
            source={"url": "u", "infoboxes": [], "tables": [], "sections": []},
        ),
        DomainCase(
            service=SeasonPipelineService,
            input_dto=SeasonDomainRecordInput(payload=SeasonRecordSections.empty()),
            source={"payload": SeasonRecordSections.empty()},
        ),
        DomainCase(
            service=CircuitPipelineService,
            input_dto=CircuitDomainRecordInput(
                source_url="u",
                infobox={},
                lap_record_rows=[],
                sections=[],
            ),
            source={
                "source_url": "u",
                "infobox": {},
                "lap_record_rows": [],
                "sections": [],
            },
        ),
    ]
)
def domain_case(request: pytest.FixtureRequest) -> DomainCase:
    return request.param


def _make_service(service_cls: type[BaseDomainPipelineService]):
    assembler = MagicMock()
    assembler.assemble.return_value = {"ok": True}
    return service_cls(assembler=assembler), assembler


def test_domain_services_share_common_base_contract(domain_case: DomainCase) -> None:
    service, _ = _make_service(domain_case.service)
    assert isinstance(service, BaseDomainPipelineService)
    assert callable(service.build_payload)
    assert callable(service.assemble)
    assert callable(service._compat_input_from_source)


def test_execute_and_run_call_same_assembler_contract(domain_case: DomainCase) -> None:
    service, assembler = _make_service(domain_case.service)

    result_execute = service.execute(domain_case.input_dto)
    result_run = service.run(domain_case.source)

    assert result_execute == {"ok": True}
    assert result_run == {"ok": True}
    assert assembler.assemble.call_count == 2


def test_build_payload_returns_expected_payload_type(domain_case: DomainCase) -> None:
    service, _ = _make_service(domain_case.service)
    payload = service.build_payload(domain_case.input_dto)

    expected_types = (
        DriverRecordDTO,
        ConstructorRecordDTO,
        SeasonPayloadDTO,
        CircuitRecordDTO,
    )
    assert isinstance(payload, expected_types)
