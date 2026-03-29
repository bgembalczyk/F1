from __future__ import annotations

from scripts.ci.adr_enforcement_policy import AdrEnforcementPolicy


def test_policy_detects_architecture_paths_and_adr_tokens() -> None:
    policy = AdrEnforcementPolicy()

    assert policy.is_architecture_path("layers/zero/executor.py")
    assert not policy.is_architecture_path("models/records/driver.py")
    assert policy.has_adr_reference("Zmiana ADR-0004")


def test_policy_marks_comments_and_whitespace_as_cosmetic() -> None:
    policy = AdrEnforcementPolicy()

    assert policy.is_cosmetic_line("   ")
    assert policy.is_cosmetic_line("# komentarz")
    assert not policy.is_cosmetic_line("return 1")


def test_policy_di_signal_threshold() -> None:
    policy = AdrEnforcementPolicy(di_required_violation_threshold=3)

    assert not policy.should_emit_di_trigger_signal(2)
    assert policy.should_emit_di_trigger_signal(3)
    assert policy.should_emit_di_trigger_signal(4, threshold=4)
    assert not policy.should_emit_di_trigger_signal(3, threshold=4)
