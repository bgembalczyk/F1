# scrapers/base/wiki_sections.py
from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag


class WikipediaSectionByIdMixin:
    """
    Mixin z logiką wycinania sekcji artykułu Wikipedii na podstawie fragmentu
    URL (np. 'Bugatti_Circuit' dla ...#Bugatti_Circuit).

    Wejście: pełny soup całego artykułu + fragment (bez '#').
    Wyjście: BeautifulSoup zawierający tylko daną sekcję (nagłówek + treść),
             lub None, jeśli sekcja nie istnieje.
    """

    @staticmethod
    def split_url_fragment(url: str) -> tuple[str, str | None]:
        base_url, fragment = (url.split("#", 1) + [None])[:2]
        if fragment is not None:
            fragment = fragment.lstrip("#").strip() or None
        return base_url, fragment

    def fetch_by_url(self, url: str) -> list[dict[str, Any]]:
        """
        Zwraca listę z pojedynczym dict (lub pustą listę) z kluczami:
        - url     – oryginalny URL (z ewentualnym fragmentem),
        - infobox – wynik F1CircuitInfoboxScraper.parse,
        - tables  – lista zparsowanych wikitabel.

        Jeżeli artykuł nie wygląda na tor/tor wyścigowy (brak odpowiednich kategorii),
        zwraca pustą listę (nie dokładamy szczegółów).
        """
        self._original_url = url
        base_url, fragment = self.split_url_fragment(url)
        self.url = base_url
        self._section_fragment = fragment
        return super().fetch()  # type: ignore[misc]

    @staticmethod
    def _find_node_by_id(soup: BeautifulSoup, fragment: str) -> Tag | None:
        """Znajduje element po ID, próbując różnych wariantów (z _, spacjami)."""
        candidates = {fragment}
        candidates.add(fragment.replace(" ", "_"))
        candidates.add(fragment.replace("_", " "))

        for cand in candidates:
            node = soup.find(id=cand)
            if node:
                return node
        return None

    @staticmethod
    def _find_header_by_text(soup: BeautifulSoup, fragment: str) -> Tag | None:
        """Znajduje nagłówek po tekście (fallback gdy nie ma ID)."""
        target_text = fragment.replace("_", " ").strip().lower()

        for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
            full_text = (h.get_text(strip=True) or "").lower()
            if full_text == target_text:
                return h

            span = h.find("span", class_="mw-headline")
            if span:
                span_text = (span.get_text(strip=True) or "").lower()
                if span_text == target_text:
                    return h
        return None

    @staticmethod
    def _extract_header_from_node(node: Tag) -> Tag | None:
        """Wyciąga nagłówek z elementu (może być sam nagłówkiem lub zawierać go)."""
        if node.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            return node
        return node.find_parent(["h1", "h2", "h3", "h4", "h5", "h6"])

    @staticmethod
    def _get_header_level(header: Tag) -> int | None:
        """Zwraca poziom nagłówka (1-6) lub None jeśli nie można określić."""
        try:
            return int(header.name[1])
        except (TypeError, ValueError, IndexError):
            return None

    @staticmethod
    def _get_heading_block(header: Tag) -> Tag:
        """Zwraca blok nagłówka (może być opakowany w mw-heading)."""
        parent = header.parent
        if isinstance(parent, Tag):
            classes = parent.get("class") or []
            if (
                "mw-heading" in classes
                and parent.find(header.name, recursive=False) is header
            ):
                return parent
        return header

    @staticmethod
    def _extract_same_level_header(sibling: Tag) -> Tag | None:
        """Wyciąga nagłówek z elementu rodzeństwa (może być bezpośredni lub w mw-heading)."""
        if sibling.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            return sibling
        elif "mw-heading" in (sibling.get("class") or []):
            return sibling.find(["h1", "h2", "h3", "h4", "h5", "h6"], recursive=False)
        return None

    @staticmethod
    def _collect_section_siblings(
        heading_block: Tag,
        header_level: int | None,
    ) -> list[Any]:
        """Zbiera wszystkie elementy rodzeństwa do następnego nagłówka tego samego poziomu."""
        collected: list[Any] = [heading_block]

        for sib in heading_block.next_siblings:
            if isinstance(sib, Tag):
                same_level_header_tag = (
                    WikipediaSectionByIdMixin._extract_same_level_header(sib)
                )

                if same_level_header_tag is not None and header_level is not None:
                    sib_level = WikipediaSectionByIdMixin._get_header_level(
                        same_level_header_tag,
                    )
                    if sib_level == header_level:
                        break

            collected.append(sib)

        return collected

    @staticmethod
    def extract_section_by_id(
        soup: BeautifulSoup,
        fragment: str,
    ) -> BeautifulSoup | None:
        """
        Wycina sekcję artykułu Wikipedii na podstawie fragmentu URL.

        1) Próbuje znaleźć element o id=fragment (oraz warianty z _ / spacjami).
        2) Jeśli się nie uda – szuka nagłówka po tekście (np. "Bugatti Circuit").
        3) Sekcję definiuje jako:
           [blok nagłówka] + wszystkie rodzeństwa aż do kolejnego nagłówka
           TEGO SAMEGO poziomu (hN).
        """
        # Znajdź nagłówek sekcji
        node = WikipediaSectionByIdMixin._find_node_by_id(soup, fragment)

        header: Tag | None = None
        if node:
            header = WikipediaSectionByIdMixin._extract_header_from_node(node)

        if header is None:
            header = WikipediaSectionByIdMixin._find_header_by_text(soup, fragment)

        if header is None:
            return None

        # Określ poziom nagłówka i blok
        header_level = WikipediaSectionByIdMixin._get_header_level(header)
        heading_block = WikipediaSectionByIdMixin._get_heading_block(header)

        # Zbierz wszystkie elementy sekcji
        collected = WikipediaSectionByIdMixin._collect_section_siblings(
            heading_block,
            header_level,
        )

        # Zbuduj HTML sekcji
        html = "".join(str(node) for node in collected)
        if not html.strip():
            return None

        section_soup = BeautifulSoup(html, "html.parser")
        return section_soup
