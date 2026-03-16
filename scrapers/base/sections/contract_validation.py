from __future__ import annotations

from typing import Any

SECTION_RESULT_KEYS = ("section_id", "section_label", "records", "metadata")


def validate_section_result_payload(payload: dict[str, Any]) -> None:
    if tuple(payload.keys()) != SECTION_RESULT_KEYS:
        msg = (
            "Section parser contract violation: expected payload keys "
            f"{SECTION_RESULT_KEYS}, got {tuple(payload.keys())}."
        )
        raise ValueError(msg)

    if not isinstance(payload["section_id"], str):
        raise ValueError("Section parser contract violation: section_id must be str.")
    if not isinstance(payload["section_label"], str):
        raise ValueError(
            "Section parser contract violation: section_label must be str.",
        )
    if not isinstance(payload["records"], list):
        raise ValueError("Section parser contract violation: records must be list.")
    if not isinstance(payload["metadata"], dict):
        raise ValueError("Section parser contract violation: metadata must be dict.")


def validate_section_payloads(payloads: list[dict[str, Any]]) -> None:
    for payload in payloads:
        validate_section_result_payload(payload)
