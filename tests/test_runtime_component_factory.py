from __future__ import annotations

from layers.orchestration.runtime_factory import RuntimeComponentFactory


def test_runtime_factory_register_and_build_instance() -> None:
    factory = RuntimeComponentFactory()
    component = object()
    factory.register_instance(
        role="runner",
        domain="drivers",
        stage="layer_one",
        instance=component,
        source="tests.component",
    )

    assert (
        factory.build(role="runner", domain="drivers", stage="layer_one") is component
    )


def test_runtime_factory_rejects_duplicate_registration_for_same_source() -> None:
    factory = RuntimeComponentFactory()
    factory.register(
        role="runner",
        domain="drivers",
        stage="layer_one",
        builder=object,
        source="tests.component",
    )

    try:
        factory.register(
            role="runner",
            domain="drivers",
            stage="layer_one",
            builder=object,
            source="tests.component",
        )
    except ValueError as exc:
        assert "Duplicate runtime registration" in str(exc)
    else:
        raise AssertionError("Expected duplicate registration to raise ValueError")


def test_runtime_factory_rejects_key_conflict_for_different_sources() -> None:
    factory = RuntimeComponentFactory()
    factory.register(
        role="runner",
        domain="drivers",
        stage="layer_one",
        builder=object,
        source="tests.component_a",
    )

    try:
        factory.register(
            role="runner",
            domain="drivers",
            stage="layer_one",
            builder=object,
            source="tests.component_b",
        )
    except ValueError as exc:
        assert "Runtime key conflict" in str(exc)
    else:
        raise AssertionError("Expected key conflict to raise ValueError")
