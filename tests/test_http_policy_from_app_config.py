from scrapers.base.helpers.http import default_http_policy


def test_default_http_policy_can_read_timeout_from_provider_env(monkeypatch) -> None:
    expected_timeout = 13
    monkeypatch.setenv("HTTP_TIMEOUT_SECONDS", str(expected_timeout))

    policy = default_http_policy()

    assert policy.timeout == expected_timeout
