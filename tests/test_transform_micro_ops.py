from scrapers.base.helpers.transform_micro_ops import expand_alias_variants
from scrapers.base.helpers.transform_micro_ops import merge_unique_preserve_order
from scrapers.base.helpers.transform_micro_ops import pop_list_field


def test_pop_list_field_normalizes_values_to_list() -> None:
    record = {"drivers": ("A", "B"), "rounds": None, "single": "x"}

    assert pop_list_field(record, "drivers") == ["A", "B"]
    assert pop_list_field(record, "rounds") == []
    assert pop_list_field(record, "single") == ["x"]
    assert "drivers" not in record
    assert "rounds" not in record
    assert "single" not in record


def test_merge_unique_preserve_order_keeps_first_occurrence() -> None:
    merged = merge_unique_preserve_order(["a", "b", "a"], ["b", "c"], ["c", "d"])

    assert merged == ["a", "b", "c", "d"]


def test_expand_alias_variants_builds_text_and_id_variants() -> None:
    normalized_ids, normalized_texts = expand_alias_variants(
        {"Career results", "Career_results", ""},
        text_normalizer=lambda value: value.replace("_", " ").lower().strip(),
    )

    assert normalized_texts == {"career results"}
    assert normalized_ids == {"career results", "career_results"}
