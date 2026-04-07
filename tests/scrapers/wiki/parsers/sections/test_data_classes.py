# ruff: noqa: E501, PLR2004

from scrapers.wiki.parsers.sections.data_classes import SectionMatchPriorities


class TestSectionMatchPriorities:
    def test_get_score_default(self):
        priorities = SectionMatchPriorities()
        assert priorities.get_score() == 1.0

    def test_get_score_exact_id(self):
        priorities = SectionMatchPriorities(exact_id_score=5.0)
        assert priorities.get_score(exact_id=True) == 5.0

    def test_get_score_exact_text(self):
        priorities = SectionMatchPriorities(exact_text_score=4.0)
        assert priorities.get_score(exact_text=True) == 4.0

    def test_get_score_fuzzy_base(self):
        priorities = SectionMatchPriorities(fuzzy_base_score=2.0)
        assert priorities.get_score() == 2.0
