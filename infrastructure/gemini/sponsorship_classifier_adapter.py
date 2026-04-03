from __future__ import annotations

from infrastructure.gemini.client import GeminiClient
from scrapers.sponsorship_liveries.helpers.paren_classifier import ParenClassifier


def build_sponsorship_paren_classifier() -> object:
    gemini_client = GeminiClient.from_key_file()
    return ParenClassifier(gemini_client=gemini_client)
