# ruff: noqa: E501, PLR2004
"""Tests for ParenClassifier covering lines 82 and 123-133."""

from unittest.mock import MagicMock

from scrapers.sponsorship_liveries.helpers_sponsorship_liveries.paren_classifier import (
    ParenClassifier,
)


def make_classifier(query_return=None, raise_exc=None):
    client = MagicMock()
    if raise_exc is not None:
        client.query.side_effect = raise_exc
    else:
        client.query.return_value = query_return
    return ParenClassifier(gemini_client=client)


class TestClassifySuccessPath:
    def test_classify_returns_normalized_result_on_success(self):
        raw = {
            "driver": ["Senna"],
            "car_model": [],
            "engine_constructor": [],
            "grand_prix": [],
        }
        classifier = make_classifier(query_return=raw)
        result = classifier.classify(
            paren_content="Senna",
            team_name="McLaren",
            year_text="1988",
        )
        assert result["driver"] == ["Senna"]
        assert result["car_model"] == []

    def test_classify_uses_headers_in_prompt(self):
        raw = {
            "driver": [],
            "car_model": [],
            "engine_constructor": [],
            "grand_prix": [],
        }
        client = MagicMock()
        client.query.return_value = raw
        classifier = ParenClassifier(gemini_client=client)
        classifier.classify(
            paren_content="something",
            team_name="Ferrari",
            year_text="1990",
            headers=["Year", "Sponsor"],
        )
        call_args = client.query.call_args[0][0]
        assert "Year" in call_args or "Sponsor" in call_args

    def test_classify_returns_empty_result_on_exception(self):
        classifier = make_classifier(raise_exc=RuntimeError("API failure"))
        result = classifier.classify(
            paren_content="boom",
            team_name="Lotus",
            year_text="1979",
        )
        assert result == {
            "driver": [],
            "car_model": [],
            "engine_constructor": [],
            "grand_prix": [],
        }


class TestNormalizeResult:
    def test_non_dict_raw_returns_empty(self):
        result = ParenClassifier._normalize_result("not a dict")
        assert result == {
            "driver": [],
            "car_model": [],
            "engine_constructor": [],
            "grand_prix": [],
        }

    def test_none_returns_empty(self):
        result = ParenClassifier._normalize_result(None)
        assert result == {
            "driver": [],
            "car_model": [],
            "engine_constructor": [],
            "grand_prix": [],
        }

    def test_list_raw_returns_empty(self):
        result = ParenClassifier._normalize_result([1, 2, 3])
        assert result == {
            "driver": [],
            "car_model": [],
            "engine_constructor": [],
            "grand_prix": [],
        }

    def test_valid_dict_with_all_keys(self):
        raw = {
            "driver": ["Hamilton", "Verstappen"],
            "car_model": ["MP4/4"],
            "engine_constructor": ["Mercedes"],
            "grand_prix": ["Monaco Grand Prix"],
        }
        result = ParenClassifier._normalize_result(raw)
        assert result["driver"] == ["Hamilton", "Verstappen"]
        assert result["car_model"] == ["MP4/4"]
        assert result["engine_constructor"] == ["Mercedes"]
        assert result["grand_prix"] == ["Monaco Grand Prix"]

    def test_non_list_value_becomes_empty_list(self):
        raw = {
            "driver": "Hamilton",
            "car_model": [],
            "engine_constructor": [],
            "grand_prix": [],
        }
        result = ParenClassifier._normalize_result(raw)
        assert result["driver"] == []

    def test_missing_keys_default_to_empty(self):
        raw = {"driver": ["Prost"]}
        result = ParenClassifier._normalize_result(raw)
        assert result["car_model"] == []
        assert result["engine_constructor"] == []
        assert result["grand_prix"] == []

    def test_falsy_items_filtered_from_lists(self):
        raw = {
            "driver": ["Senna", "", None, "Prost"],
            "car_model": [],
            "engine_constructor": [],
            "grand_prix": [],
        }
        result = ParenClassifier._normalize_result(raw)
        assert result["driver"] == ["Senna", "Prost"]
