# ruff: noqa: ARG002, EM101, PLC0415, PLR2004, RUF005, S108
from __future__ import annotations

from pathlib import Path

from scrapers.base.orchestration.models import AuditEntry
from scrapers.base.orchestration.models import ResolvedInput
from scrapers.base.orchestration.models import StepDeclaration
from tests.support.step_orchestrator_assertions import (
    assert_section_source_adapter_falls_back_to_raw,
)


class FakeInputResolver:
    def __init__(self) -> None:
        self.value = ResolvedInput(
            records=[{"value": 1}],
            source_path=Path("/tmp/input.json"),
        )

    def resolve(self, step: StepDeclaration, domain: str) -> ResolvedInput:
        return self.value


class FakeCheckpointRepository:
    def __init__(self) -> None:
        self.saved = []

    def save(self, step, domain, input_path, input_records, execution):
        self.saved.append(
            (step.step_id, domain, input_path, input_records, execution.records),
        )
        return Path(f"/tmp/step_{step.step_id}_{domain}.json")


class FakeAuditRepository:
    def __init__(self) -> None:
        self.entries: list[AuditEntry] = []

    def append(self, entry: AuditEntry) -> None:
        self.entries.append(entry)

    def write_regression_report(self, report_path: Path) -> Path:
        return report_path


def test_input_resolver_contract_returns_records_and_path(tmp_path: Path) -> None:
    assert_section_source_adapter_falls_back_to_raw(tmp_path)
