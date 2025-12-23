# scrapers/base/wiki_sections.py
from typing import Any, Dict, List, Optional, Tuple

from bs4 import BeautifulSoup, Tag

from scrapers.circuits.helpers.article_validation import is_circuit_like_article


class WikipediaSectionByIdMixin:
    """
    Mixin z logiką wycinania sekcji artykułu Wikipedii na podstawie fragmentu
    URL (np. 'Bugatti_Circuit' dla ...#Bugatti_Circuit).

    Wejście: pełny soup całego artykułu + fragment (bez '#').
    Wyjście: BeautifulSoup zawierający tylko daną sekcję (nagłówek + treść),
             lub None, jeśli sekcja nie istnieje.
    """

    @staticmethod
    def split_url_fragment(url: str) -> Tuple[str, Optional[str]]:
        base_url, fragment = (url.split("#", 1) + [None])[:2]
        if fragment is not None:
            fragment = fragment.lstrip("#").strip() or None
        return base_url, fragment

    def fetch_by_url(self, url: str) -> List[Dict[str, Any]]:
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
    def _is_circuit_like_article(soup: BeautifulSoup) -> bool:
        return is_circuit_like_article(soup)

    @staticmethod
    def _extract_section_by_id(
        soup: BeautifulSoup,
        fragment: str,
    ) -> Optional[BeautifulSoup]:
        """
        Wycina sekcję artykułu Wikipedii na podstawie fragmentu URL.

        1) Próbuje znaleźć element o id=fragment (oraz warianty z _ / spacjami).
        2) Jeśli się nie uda – szuka nagłówka po tekście (np. "Bugatti Circuit").
        3) Sekcję definiuje jako:
           [blok nagłówka] + wszystkie rodzeństwa aż do kolejnego nagłówka
           TEGO SAMEGO poziomu (hN).
        """
        candidates = {fragment}
        candidates.add(fragment.replace(" ", "_"))
        candidates.add(fragment.replace("_", " "))

        node: Optional[Tag] = None
        for cand in candidates:
            node = soup.find(id=cand)
            if node:
                break

        header: Optional[Tag] = None

        if node:
            if node.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
                header = node
            else:
                header = node.find_parent(["h1", "h2", "h3", "h4", "h5", "h6"])

        if header is None:
            target_text = fragment.replace("_", " ").strip().lower()

            for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
                full_text = (h.get_text(strip=True) or "").lower()
                if full_text == target_text:
                    header = h
                    break

                span = h.find("span", class_="mw-headline")
                if span:
                    span_text = (span.get_text(strip=True) or "").lower()
                    if span_text == target_text:
                        header = h
                        break

        if header is None:
            return None

        try:
            header_level = int(header.name[1])
        except (TypeError, ValueError, IndexError):
            header_level = None

        heading_block: Tag = header
        parent = header.parent
        if isinstance(parent, Tag):
            classes = parent.get("class") or []
            if (
                "mw-heading" in classes
                and parent.find(header.name, recursive=False) is header
            ):
                heading_block = parent

        collected: List[Any] = [heading_block]

        for sib in heading_block.next_siblings:
            if isinstance(sib, Tag):
                same_level_header_tag: Optional[Tag] = None

                if sib.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
                    same_level_header_tag = sib
                elif "mw-heading" in (sib.get("class") or []):
                    h_child = sib.find(
                        ["h1", "h2", "h3", "h4", "h5", "h6"], recursive=False
                    )
                    if h_child is not None:
                        same_level_header_tag = h_child

                if same_level_header_tag is not None and header_level is not None:
                    try:
                        sib_level = int(same_level_header_tag.name[1])
                    except (TypeError, ValueError, IndexError):
                        sib_level = None

                    if sib_level == header_level:
                        break

            collected.append(sib)

        html = "".join(str(node) for node in collected)
        if not html.strip():
            return None

        section_soup = BeautifulSoup(html, "html.parser")
        return section_soup
