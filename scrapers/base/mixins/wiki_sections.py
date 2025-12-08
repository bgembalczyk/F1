# scrapers/base/wiki_sections.py
from __future__ import annotations

from typing import Any, List, Optional

from bs4 import BeautifulSoup, Tag


class WikipediaSectionByIdMixin:
    """
    Mixin z logiką wycinania sekcji artykułu Wikipedii na podstawie fragmentu
    URL (np. 'Bugatti_Circuit' dla ...#Bugatti_Circuit).

    Wejście: pełny soup całego artykułu + fragment (bez '#').
    Wyjście: BeautifulSoup zawierający tylko daną sekcję (nagłówek + treść),
             lub None, jeśli sekcja nie istnieje.
    """

    def _extract_section_by_id(
        self,
        soup: BeautifulSoup,
        fragment: str,
    ) -> Optional[BeautifulSoup]:
        """
        1) Próbuje znaleźć element o id=fragment (oraz warianty z _ / spacjami).
        2) Jeśli się nie uda – szuka nagłówka po tekście (np. "Bugatti Circuit").
        3) Sekcję definiuje jako:
           [blok nagłówka] + wszystkie rodzeństwa aż do kolejnego nagłówka
           TEGO SAMEGO poziomu (hN).
        """

        # --- 1) znajdź węzeł po id (z normalizacją _) ---
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
            # przypadek: id jest BEZPOŚREDNIO na <hN>
            if node.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
                header = node
            else:
                header = node.find_parent(["h1", "h2", "h3", "h4", "h5", "h6"])

        # --- 2) fallback: szukanie nagłówka po tekście ---
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

        # Poziom nagłówka (np. 2 dla h2)
        try:
            header_level = int(header.name[1])
        except (TypeError, ValueError, IndexError):
            header_level = None

        # --- 3) uwzględnij wrapper <div class="mw-heading ..."> jeśli jest ---
        heading_block: Tag = header
        parent = header.parent
        if isinstance(parent, Tag):
            classes = parent.get("class") or []
            if "mw-heading" in classes and parent.find(
                header.name, recursive=False
            ) is header:
                heading_block = parent

        # UWAGA: nie przenosimy heading_block do nowego soup-a przed zebraniem rodzeństw.
        collected: List[Any] = [heading_block]

        # --- 4) zbierz rodzeństwa aż do nagłówka tego samego poziomu ---
        for sib in heading_block.next_siblings:
            if isinstance(sib, Tag):
                same_level_header_tag: Optional[Tag] = None

                # Przypadek 1: nagłówek bez wrappera
                if sib.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
                    same_level_header_tag = sib

                # Przypadek 2: wrapper <div class="mw-heading ..."><hN>...</hN></div>
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
                        # doszliśmy do następnej sekcji tego samego poziomu
                        break

            collected.append(sib)

        html = "".join(str(node) for node in collected)
        if not html.strip():
            return None

        section_soup = BeautifulSoup(html, "html.parser")
        return section_soup
