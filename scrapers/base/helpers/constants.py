import re

from scrapers.base.helpers.common_config import ScraperCommonConfig

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
DATE_RANGE_SPLIT = re.compile(r"\s*[-\u2013]\s*")
DATE_FORMATS = [
    "%d %B %Y",  # 7 June 2019
    "%d %b %Y",  # 7 Jun 2019
    "%B %d, %Y",  # June 7, 2019
    "%b %d, %Y",  # Jun 7, 2019
]

SHORT_YEAR_LEN = 2
MIN_URLS_FOR_PATTERN = 2

NON_ALPHANUM_PATTERN = re.compile(r"[^0-9a-zA-Z]+")
UNDERSCORE_PATTERN = re.compile(r"_+")

HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
HEADING_AND_TABLE_TAGS = [*list(HEADING_TAGS), "table"]

DEFAULT_CONFIG_PROFILE = "soft_seed"

COMMON_CONFIG_PROFILES: dict[str, ScraperCommonConfig] = {
    "soft_seed": ScraperCommonConfig(
        include_urls=True,
        normalize_empty_values=True,
        validation_mode="soft",
    ),
    "strict_seed": ScraperCommonConfig(
        include_urls=True,
        normalize_empty_values=False,
        validation_mode="hard",
    ),
    "details": ScraperCommonConfig(
        include_urls=True,
        normalize_empty_values=True,
        validation_mode="soft",
    ),
}

DOMAIN_CONFIG_PROFILE_OVERRIDES: dict[str, dict[str, ScraperCommonConfig]] = {
    "circuits": {
        "soft_seed": ScraperCommonConfig(
            include_urls=True,
            normalize_empty_values=False,
            validation_mode="soft",
        ),
    },
}
