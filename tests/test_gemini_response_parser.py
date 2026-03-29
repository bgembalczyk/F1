import pytest

from infrastructure.gemini.response_parser import GeminiResponseParser


def test_parse_returns_mapped_json() -> None:
    parser = GeminiResponseParser()
    api_response = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": '{"ok": true, "value": 7}',
                        },
                    ],
                },
            },
        ],
    }

    assert parser.parse(api_response) == {"ok": True, "value": 7}


def test_parse_raises_when_missing_text() -> None:
    parser = GeminiResponseParser()

    with pytest.raises(RuntimeError, match="nie zwróciło pola"):
        parser.parse({"candidates": []})


def test_parse_raises_when_text_not_json() -> None:
    parser = GeminiResponseParser()
    api_response = {
        "candidates": [{"content": {"parts": [{"text": "not-json"}]}}],
    }

    with pytest.raises(RuntimeError, match="nie jest poprawnym JSON-em"):
        parser.parse(api_response)
