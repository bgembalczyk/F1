# ruff: noqa: PT011
from __future__ import annotations

import pytest

from scrapers.circuits.postprocess.contract import CircuitSectionContractPostProcessor
from scrapers.constructors.postprocess.contract import (
    ConstructorSectionContractPostProcessor,
)


def test_constructor_postprocess_validates_section_payload_contract() -> None:
    processor = ConstructorSectionContractPostProcessor()

    with pytest.raises(ValueError):
        processor.post_process(
            [
                {
                    "sections": [
                        {
                            "section_id": "history",
                            "records": [],
                            "section_label": "History",
                            "metadata": {},
                        },
                    ],
                },
            ],
        )


def test_circuit_postprocess_accepts_valid_section_payload_contract() -> None:
    processor = CircuitSectionContractPostProcessor()
    records = processor.post_process(
        [
            {
                "sections": [
                    {
                        "section_id": "events",
                        "section_label": "Events",
                        "records": [],
                        "metadata": {},
                    },
                ],
            },
        ],
    )
    assert records
