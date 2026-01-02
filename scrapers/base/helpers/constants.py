import re

REF_RE = re.compile(r"\[\s*[^]]+\s*]")

LANG_CODES = {
    "en",
    "es",
    "fr",
    "de",
    "it",
    "pt",
    "pl",
    "ru",
    "cs",
    "sk",
    "hu",
    "ro",
    "bg",
    "sr",
    "hr",
    "sl",
    "nl",
    "sv",
    "no",
    "da",
    "fi",
    "el",
    "tr",
    "ar",
    "he",
    "id",
    "ms",
    "th",
    "vi",
    "ja",
    "ko",
    "zh",
    "uk",
    "ca",
    "eu",
    "gl",
}

TIME_SECONDS_RE = re.compile(r"^\s*(?:(\d+):)?(\d+(?:\.\d+)?)\s*$")
TIME_KEY_RE = re.compile(r"(?:(\d+):)?(\d+(?:\.\d+)?)")
DATE_RANGE_SPLIT = re.compile(r"\s*[–-]\s*")
DATE_FORMATS = [
    "%d %B %Y",  # 7 June 2019
    "%d %b %Y",  # 7 Jun 2019
    "%B %d, %Y",  # June 7, 2019
    "%b %d, %Y",  # Jun 7, 2019
]
