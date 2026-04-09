import sys
from unittest.mock import MagicMock

# Mock bs4
sys.modules["bs4"] = MagicMock()

from scrapers.sponsorship_liveries.columns_sponsorship_liveries.sponsor import SponsorColumn  # noqa: E402

links = [{"text": "Sponsor A"}, {"text": "Sponsor D —"}]
best = SponsorColumn._find_matching_link("Sponsor D — ", links)
print(f"Matched: {best}")

best_not_matching = SponsorColumn._find_matching_link("Sponsor D — NotMatching", links)
print(f"Not Matched (should be None or not Sponsor D): {best_not_matching}")
