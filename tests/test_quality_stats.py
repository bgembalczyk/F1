from validation.issue import ValidationIssue
from validation.quality_stats import QualityStats


def test_record_accepted_increments_only_total_records() -> None:
    stats = QualityStats()

    stats.record_accepted()

    assert stats.total_records == 1
    assert stats.rejected_records == 0
    assert stats.accepted_records == 1


def test_record_rejected_tracks_missing_and_type_issues() -> None:
    stats = QualityStats()

    stats.record_rejected(
        [
            ValidationIssue.missing("name"),
            ValidationIssue.null("name"),
            ValidationIssue.type_error("age", "int", "str"),
            ValidationIssue.custom("ignore me"),
        ],
    )

    assert stats.total_records == 1
    assert stats.rejected_records == 1
    assert stats.accepted_records == 0
    assert stats.missing == {"name": 2}
    assert stats.types == {"age": 1}


def test_record_rejected_accumulates_multiple_calls() -> None:
    stats = QualityStats()

    stats.record_rejected([ValidationIssue.missing("country")])
    stats.record_rejected([ValidationIssue.type_error("country", "str", "int")])

    assert stats.total_records == 2
    assert stats.rejected_records == 2
    assert stats.missing == {"country": 1}
    assert stats.types == {"country": 1}
