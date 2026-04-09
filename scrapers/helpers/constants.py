import re

from scrapers.common_config import ScraperCommonConfig

SHORT_YEAR_LEN = 2
MIN_URLS_FOR_PATTERN = 2
DETAILS_PARTS_COUNT_MANY = 4
DETAILS_PARTS_COUNT_MEDIUM = 3
DETAILS_PARTS_COUNT_FEW = 2
DETAILS_PARTS_BONUS_4 = 5
DETAILS_PARTS_BONUS_3 = 2
DETAILS_PARTS_BONUS_2 = 1
DETAILS_MIN_SCORE_WITHOUT_COMMA = 3

DEFAULT_CONFIG_PROFILE = "soft_seed"
GRAND_PRIX_KEYWORD = "grand prix"
GRAND_PRIX_NAVBOX_TEMPLATE = "Template:Formula_One_Grands_Prix"
DEFAULT_CHAMPIONSHIP = "formula_one_world_championship"
UNKNOWN_CHAMPIONSHIP = "unknown"


REF_RE = re.compile(r"\[\s*[^]]+\s*]")
YEAR_RANGE_RE = re.compile(r"\b(\d{4})\s*[-\u2013]\s*(\d{2,4})\b")
YEAR_EXT_RE = re.compile(r"\b(\d{4})\b")
TIME_SECONDS_RE = re.compile(r"^\s*(?:(\d+):)?(\d+(?:\.\d+)?)\s*$")
TIME_KEY_RE = re.compile(r"(?:(\d+):)?(\d+(?:\.\d+)?)")
DATE_RANGE_SPLIT = re.compile(r"\s*[-\u2013]\s*")
DATE_ISO_FULL_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
DATE_ISO_MONTH_RE = re.compile(r"\d{4}-\d{2}")
DATE_ISO_YEAR_RE = re.compile(r"\d{4}")
YEAR_RE = re.compile(r"\b(1[89]\d{2}|20\d{2})\b")
NON_ALPHANUM_PATTERN = re.compile(r"[^0-9a-zA-Z]+")
UNDERSCORE_PATTERN = re.compile(r"_+")
# Year-only link text - e.g. "2004" or "2005"
YEAR_RE_SPONSOR = re.compile(r"^\d{4}$")

year_re = re.compile(r"\b\d{4}\b")

year_range_re = re.compile(r"\b(\d{4})\s*[-\-]\s*(\d{4})\b")

# Matches abbreviated end-year ranges like "1979-83" or "1977-82".
# The end year is 2 digits and must NOT be followed by another digit.
year_range_abbrev_re = re.compile(r"\b(\d{4})\s*[-\-]\s*(\d{2})(?!\d)")

decade_re = re.compile(r"\b(\d{3})0s\b")

POSSESSIVE_PAREN_RE = re.compile(r"\([^)]*'s[^)]*\)\s*$")

# Regex for possessive colour-note suffixes with driver names.
POSSESSIVE_COLOUR_RE = re.compile(r"^(.*?)\s*\(([^)']*)'s[^)]*\)\s*$")

SPONSOR_PAREN_GROUP_RE = re.compile(r"\(([^)]+)\)")
SPONSOR_PAREN_REMOVE_RE = re.compile(r"\s*\([^)]*\)")

PARAM_MATCH_ONLY_ONWARD_RE = re.compile(r"\b(only|onwards?)\b", flags=re.IGNORECASE)
PARAM_MATCH_FROM_RE = re.compile(r"^\s*from\s+", flags=re.IGNORECASE)
# Regex to remove whitespace and dashes from string remainders.
REMAINDER_CLEANUP_RE = re.compile(r"[\s\-—]")

HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}

COLOUR_KEYS = {
    "main_colours",
    "additional_colours",
}

season_headers = {
    "year",
    "years",
    "season",
    "seasons",
}

SPONSOR_KEYS = {
    "main_sponsors",
    "additional_major_sponsors",
    "livery_sponsors",
    "livery_principal_sponsors",
}


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

LANG_ALT = "|".join(sorted(LANG_CODES, key=len, reverse=True))
LANG_SUFFIX_NO_PAREN_RE = re.compile(rf"\s+({LANG_ALT})\s*$", flags=re.IGNORECASE)
LANG_SUFFIX_PAREN_RE = re.compile(
    rf"\s*\(\s*({LANG_ALT})\s*\)\s*$",
    flags=re.IGNORECASE,
)

HEADING_AND_TABLE_TAGS = [*list(HEADING_TAGS), "table"]


DATE_FORMATS = [
    "%d %B %Y",  # 7 June 2019
    "%d %b %Y",  # 7 Jun 2019
    "%B %d, %Y",  # June 7, 2019
    "%b %d, %Y",  # Jun 7, 2019
]

CIRCUIT_KEYWORDS = [
    "circuit",
    "race track",
    "racetrack",
    "speedway",
    "raceway",
    "motor racing",
    "motorsport venue",
]

BACKGROUND_MAP = {
    "ffffcc": "pre_war_european_championship",
    "d0ffb0": "pre_war_world_manufacturers_championship",
    "ffcccc": "non_championship",
}


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


PROMPT_TEMPLATE = """
Analizujesz tabelę Wikipedii o historycznych malowaniach sponsorów w Formule 1.

Określ, czego dotyczy ta adnotacja.
Odpowiedz wyłącznie w formacie JSON z następującymi kluczami
(każdy zawiera listę elementów lub pustą listę []):
- "driver": lista kierowców F1, których dotyczy adnotacja (imię i nazwisko)
- "car_model": lista modeli bolidów/samochodów wyścigowych
- "engine_constructor": lista konstruktorów/dostawców silników
- "grand_prix": lista konkretnych wyścigów Grand Prix
  (pełna nazwa, np. "Monaco Grand Prix")

Przykład odpowiedzi:
{{
  "driver": [],
  "car_model": ["Dallara F188"],
  "engine_constructor": [],
  "grand_prix": []
}}

Odpowiedz tylko poprawnym JSON, bez dodatkowego tekstu.

Nie uzupełniaj za pomocą własnej wiedzy; odpowiedz tylko na podstawie
poniższych informacji. Jeśli danej informacji nie da się wywnioskować
wyłącznie z tych danych, pozostaw odpowiednią kategorię pustą.
Jeśli treść ewidentnie sugeruje przeczenie, to znaczy,
że nie dotyczy tego o czym wspomina, więc nie należy tego wpisywać do kategorii.

Zespół F1: {team_name}

W kolumnie "Year" (rok) przy wpisie roku {year_text!r}
pojawia się adnotacja w nawiasie: {paren_content!r}
"""
