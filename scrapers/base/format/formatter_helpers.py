from typing import TYPE_CHECKING
from typing import Any

from models.mappers.serialization import to_dict_list

if TYPE_CHECKING:
    from scrapers.base.results import ScrapeResult


def extract_data(result: "ScrapeResult | list[dict[str, Any]]") -> list[dict[str, Any]]:
    """
    Główna, spójna ścieżka ekstrakcji danych:
    - zawsze zwracamy list[dict[str,Any]]
    - wykorzystujemy to_dict_list (Twoja wspólna warstwa serializacji)
    """
    if isinstance(result, list):
        return to_dict_list(result)
    return to_dict_list(list(result.data))
