from layers.orchestration.record_classifier import RecordClassifier
from layers.orchestration.record_classifier import RecordClassifierInput


def test_classifier_returns_expected_chains_for_drivers() -> None:
    classifier = RecordClassifier()

    decision = classifier.classify(
        RecordClassifierInput(domain="drivers", source_name="f1_drivers.json"),
    )

    assert decision.domain == "drivers"
    assert decision.source_type == "drivers_default"
    assert decision.transform_chain == ("drivers_domain",)
    assert decision.postprocess_chain == (
        "merge_duplicate_drivers",
        "sort_drivers_by_name",
    )


def test_classifier_adds_global_tyre_transform_chain() -> None:
    classifier = RecordClassifier()

    decision = classifier.classify(
        RecordClassifierInput(
            domain="seasons",
            source_name="f1_tyre_manufacturers_by_season.json",
        ),
    )

    assert decision.source_type == "tyre_manufacturers"
    assert decision.transform_chain == ("tyre_manufacturers",)


def test_classifier_detects_special_constructor_sources() -> None:
    classifier = RecordClassifier()

    decision = classifier.classify(
        RecordClassifierInput(
            domain="constructors",
            source_name="f1_indianapolis_only_constructors.json",
        ),
    )

    assert decision.source_type == "indianapolis_only"
    assert decision.transform_chain == ("constructor_domain",)
    assert decision.postprocess_chain == ("sort_constructors_by_name",)
