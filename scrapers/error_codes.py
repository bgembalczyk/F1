from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ErrorCodeDefinition:
    """Opis kodu diagnostycznego dla wyjątków i warningów pipeline."""

    code_id: str
    symbolic_code: str
    short_description: str
    context_hint: str
    recommended_action: str


ERROR_CODE_CATALOG: dict[str, ErrorCodeDefinition] = {
    "source.domain_parse_error": ErrorCodeDefinition(
        code_id="D001",
        symbolic_code="source.domain_parse_error",
        short_description="Błąd parsowania danych domenowych",
        context_hint="Sekcja/rekord domenowy nie spełnia oczekiwanego formatu",
        recommended_action="Zweryfikuj strukturę sekcji i dopasuj parser domenowy.",
    ),
    "source.not_found": ErrorCodeDefinition(
        code_id="D002",
        symbolic_code="source.not_found",
        short_description="Brak oczekiwanego elementu źródła",
        context_hint="Nie znaleziono listy/sekcji/tabeli wymaganej przez scraper",
        recommended_action="Sprawdź selektory i aliasy sekcji dla danej domeny.",
    ),
    "transport.error": ErrorCodeDefinition(
        code_id="M002",
        symbolic_code="transport.error",
        short_description="Błąd transportu/sieci",
        context_hint="Pobieranie HTML lub request do źródła nie powiódł się",
        recommended_action="Sprawdź dostępność URL, timeout/retry i politykę HTTP.",
    ),
    "source.parse_error": ErrorCodeDefinition(
        code_id="P001",
        symbolic_code="source.parse_error",
        short_description="Błąd parsowania źródła",
        context_hint="Parser nie potrafi zmapować HTML na rekordy pośrednie",
        recommended_action="Dodaj obsługę wariantu HTML lub fallback parsera.",
    ),
    "validation.error": ErrorCodeDefinition(
        code_id="V003",
        symbolic_code="validation.error",
        short_description="Błąd walidacji rekordu",
        context_hint="Rekord nie przechodzi walidatorów kontraktu danych",
        recommended_action="Dostosuj mapowanie pól albo reguły walidacji.",
    ),
    "validation.soft_reject": ErrorCodeDefinition(
        code_id="V004",
        symbolic_code="validation.soft_reject",
        short_description="Odrzucony rekord w trybie soft",
        context_hint="Walidacja ostrzegła, ale pipeline kontynuuje przetwarzanie",
        recommended_action=(
            "Przeanalizuj warningi walidacji i popraw jakość danych wejściowych."
        ),
    ),
    "pipeline.error": ErrorCodeDefinition(
        code_id="M001",
        symbolic_code="pipeline.error",
        short_description="Niezmapowany błąd pipeline",
        context_hint="Wyjątek nie został sklasyfikowany do konkretnej kategorii",
        recommended_action="Dodaj mapowanie wyjątku w normalize_pipeline_error.",
    ),
}


UNKNOWN_ERROR_CODE = ErrorCodeDefinition(
    code_id="U000",
    symbolic_code="unknown.error",
    short_description="Nieznany kod błędu",
    context_hint="Brak definicji kodu w katalogu",
    recommended_action="Uzupełnij ERROR_CODE_CATALOG o brakujący kod.",
)


def resolve_error_code(code: str | None) -> ErrorCodeDefinition:
    if not code:
        return UNKNOWN_ERROR_CODE
    return ERROR_CODE_CATALOG.get(code, UNKNOWN_ERROR_CODE)
