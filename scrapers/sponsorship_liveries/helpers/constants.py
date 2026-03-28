import re

# Year-only link text - e.g. "2004" or "2005"
YEAR_RE = re.compile(r"^\d{4}$")

year_re = re.compile(r"\b\d{4}\b")

year_range_re = re.compile(r"\b(\d{4})\s*[-\-]\s*(\d{4})\b")

# Matches abbreviated end-year ranges like "1979-83" or "1977-82".
# The end year is 2 digits and must NOT be followed by another digit.
year_range_abbrev_re = re.compile(r"\b(\d{4})\s*[-\-]\s*(\d{2})(?!\d)")

decade_re = re.compile(r"\b(\d{3})0s\b")

POSSESSIVE_PAREN_RE = re.compile(r"\([^)]*'s[^)]*\)\s*$")

# Regex for possessive colour-note suffixes with driver names.
POSSESSIVE_COLOUR_RE = re.compile(r"^(.*?)\s*\(([^)']*)'s[^)]*\)\s*$")


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

COLOUR_KEYS = {
    "main_colours",
    "additional_colours",
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
