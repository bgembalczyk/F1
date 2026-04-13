import pytest

from scrapers.section.contract_validation import is_legacy_section_payload
from scrapers.section.contract_validation import validate_section_result_payload
from tests.scrapers.base.sections.helpers import valid_payload


def test_is_legacy_section_payload_detects_legacy_keys() -> None:
    assert is_legacy_section_payload({"section": "x"}) is True
    assert is_legacy_section_payload({"items": []}) is True
    assert is_legacy_section_payload(valid_payload()) is False


def test_validate_section_payload_rejects_invalid_key_order_or_set() -> None:
    payload = {
        "section_label": "Career results",
        "section_id": "career_results",
        "records": [],
        "metadata": {},
    }

    with pytest.raises(TypeError, match="expected payload keys"):
        validate_section_result_payload(payload)


def test_validate_section_payload_rejects_non_string_section_id() -> None:
    payload = valid_payload()
    payload["section_id"] = 123

    with pytest.raises(TypeError, match="section_id must be str"):
        validate_section_result_payload(payload)


def test_validate_section_payload_rejects_non_string_section_label() -> None:
    payload = valid_payload()
    payload["section_label"] = 123

    with pytest.raises(TypeError, match="section_label must be str"):
        validate_section_result_payload(payload)


def test_validate_section_payload_rejects_non_list_records() -> None:
    payload = valid_payload()
    payload["records"] = "not-a-list"

    with pytest.raises(TypeError, match="records must be list"):
        validate_section_result_payload(payload)


def test_validate_section_payload_rejects_non_dict_metadata() -> None:
    payload = valid_payload()
    payload["metadata"] = "not-a-dict"

    with pytest.raises(TypeError, match="metadata must be dict"):
        validate_section_result_payload(payload)


def test_validate_section_payload_accepts_valid_contract() -> None:
    validate_section_result_payload(valid_payload())
