import pytest

from infrastructure.http_client.policies.http_status import HttpStatusPolicy


@pytest.mark.parametrize(
    ("status_code", "expected"),
    [
        (200, False),
        (204, False),
        (301, False),
        (399, False),
        (400, True),
        (404, True),
        (500, True),
        (599, True),
    ],
)
def test_http_status_policy_error_contract(status_code: int, expected: bool) -> None:
    assert HttpStatusPolicy.is_error(status_code) is expected


@pytest.mark.parametrize(
    ("status_code", "expected"),
    [
        (200, False),
        (301, False),
        (400, False),
        (403, False),
        (404, False),
        (429, True),
        (500, True),
        (503, True),
        (599, True),
    ],
)
def test_http_status_policy_retryable_contract(status_code: int, expected: bool) -> None:
    assert HttpStatusPolicy.is_retryable(status_code) is expected
