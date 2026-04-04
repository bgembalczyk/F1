import pytest

from scrapers.base.table.columns.helpers.link_lookup import build_link_lookup


@pytest.mark.parametrize(
    ("links", "expected_keys", "expected_bucket_sizes"),
    [
        (
            [
                {"text": " McLaren ", "url": "https://example.com/mclaren"},
                {"text": "mclaren", "url": "https://example.com/mclaren-history"},
                {"text": "Ferrari", "url": "https://example.com/ferrari"},
            ],
            ["mclaren", "ferrari"],
            {"mclaren": 2, "ferrari": 1},
        ),
        (
            [
                {"text": None, "url": "https://example.com/empty-none"},
                {"text": "", "url": "https://example.com/empty-str"},
                {"text": "   ", "url": "https://example.com/spaces"},
                {"text": "Renault", "url": "https://example.com/renault"},
            ],
            ["", "renault"],
            {"": 1, "renault": 1},
        ),
    ],
)
def test_build_link_lookup_handles_duplicates_and_weird_text_values(
    links,
    expected_keys,
    expected_bucket_sizes,
) -> None:
    lookup = build_link_lookup(links)

    assert list(lookup.keys()) == expected_keys
    for key, expected_size in expected_bucket_sizes.items():
        assert len(lookup[key]) == expected_size


def test_build_link_lookup_returns_empty_for_empty_input() -> None:
    assert build_link_lookup([]) == {}
