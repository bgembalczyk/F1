from __future__ import annotations

import json
from pathlib import Path

from scrapers.base.orchestration import AuditEntry
from scrapers.base.orchestration import CheckpointPayloadFactory
from scrapers.base.orchestration import ExecutedStep
from scrapers.base.orchestration import JsonCheckpointRepository
from scrapers.base.orchestration import ParserStepExecutor
from scrapers.base.orchestration import ResolvedInput
from scrapers.base.orchestration import SectionSourceAdapter
from scrapers.base.orchestration import StepDeclaration
from scrapers.base.orchestration import StepOrchestrator


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
    source = tmp_path / "data" / "raw" / "drivers" / "drivers.json"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(json.dumps([{"driver": {"url": "x"}}]), encoding="utf-8")

    resolver = SectionSourceAdapter(base_dir=tmp_path / "data")
    step = StepDeclaration(1, "layer1", "drivers", lambda rows: rows, "checkpoints")

    resolved = resolver.resolve(step, "drivers")

    assert resolved.source_path == source
    assert resolved.records == [{"driver": {"url": "x"}}]


def test_step_executor_contract_handles_success_and_error() -> None:
    executor = ParserStepExecutor()
    step_ok = StepDeclaration(
        1,
        "layer1",
        "x",
        lambda rows: rows + [{"ok": True}],
        "checkpoints",
    )
    ok = executor.execute(step_ok, [{"value": 1}])
    assert ok.errors == []
    assert ok.records[-1] == {"ok": True}

    def _boom(_rows):
        raise ValueError("boom")

    step_fail = StepDeclaration(2, "layer1", "x", _boom, "checkpoints")
    failed = executor.execute(step_fail, [{"value": 1}])
    assert failed.records == []
    assert failed.errors == ["boom"]


def test_checkpoint_repository_contract_writes_payload(tmp_path: Path) -> None:
    repo = JsonCheckpointRepository(
        base_dir=tmp_path / "data",
        payload_factory=CheckpointPayloadFactory(),
    )
    step = StepDeclaration(3, "layer2", "x", lambda rows: rows, "checkpoints")
    execution = ExecutedStep(records=[{"k": "v"}], errors=[], duration_ms=1.2)

    output_path = repo.save(
        step,
        "drivers",
        Path("/tmp/source.json"),
        [{"in": 1}],
        execution,
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["metadata"]["metrics"]["input_records"] == 1
    assert payload["metadata"]["metrics"]["output_records"] == 1
    assert payload["records"] == [{"k": "v"}]


def test_audit_repository_contract_appends_and_reports(tmp_path: Path) -> None:
    from scrapers.base.orchestration import StepAuditTrail

    audit = StepAuditTrail(
        json_path=tmp_path / "data" / "checkpoints" / "step_audit.json",
        csv_path=tmp_path / "data" / "checkpoints" / "step_audit.csv",
    )
    audit.append(
        AuditEntry(
            timestamp="2024-01-01T00:00:00+00:00",
            step_id=1,
            layer="layer1",
            domain="drivers",
            input_path="in",
            output_path="out",
            input_records=1,
            output_records=1,
            errors=[],
            duration_ms=2.5,
        ),
    )

    report = audit.write_regression_report(
        tmp_path / "data" / "checkpoints" / "report.md",
    )
    assert report.exists()
    assert "# Step Regression Audit Report" in report.read_text(encoding="utf-8")


def test_orchestrator_integration_with_fake_repositories() -> None:
    input_resolver = FakeInputResolver()
    checkpoint_repository = FakeCheckpointRepository()
    audit_repository = FakeAuditRepository()

    orchestrator = StepOrchestrator(
        input_resolver=input_resolver,
        checkpoint_repository=checkpoint_repository,
        audit_repository=audit_repository,
    )

    step = StepDeclaration(
        7,
        "layer7",
        "any",
        lambda rows: [{"value": rows[0]["value"] + 1}],
        "checkpoints",
    )
    result = orchestrator.run(step, "drivers")

    assert result.output_path == "/tmp/step_7_drivers.json"
    assert checkpoint_repository.saved[0][0] == 7
    assert checkpoint_repository.saved[0][4] == [{"value": 2}]
    assert len(audit_repository.entries) == 1
    assert audit_repository.entries[0].step_id == 7
