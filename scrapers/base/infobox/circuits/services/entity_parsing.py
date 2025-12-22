import re
from typing import Any, Dict, List, Optional, Union

from models.records import LinkRecord
from scrapers.base.helpers.wiki import (
    is_language_marker_link,
    is_wikipedia_redlink,
)
from scrapers.base.infobox.circuits.services.text_processing import (
    CircuitTextProcessing,
)


class CircuitEntityParser(CircuitTextProcessing):
    """Parsowanie linkowanych encji (architect, owner, website itp.)."""

    def parse_linked_entity(
        self,
        row: Optional[Dict[str, Any]],
    ) -> Optional[Union[Dict[str, Any], str, List[Dict[str, Any]]]]:
        if not row:
            return None

        text = (self._get_text(row) or "").strip()
        if not text:
            return None

        links = row.get("links") or []

        def _clean_link(link_record: LinkRecord) -> Optional[LinkRecord]:
            link_text = (link_record.get("text") or "").strip()
            if not link_text:
                return None

            url = link_record.get("url")

            # marker językowy typu "it" + https://it.wikipedia.org/... -> OUT
            if is_language_marker_link(link_text, url):
                return None

            # redlink -> url None, zostaw tekst
            if is_wikipedia_redlink(url):
                url = None

            cleaned_link: LinkRecord = {"text": link_text, "url": url}
            return cleaned_link

        # wiele linków -> lista (pomijamy językowe)
        if len(links) > 1:
            out: List[Dict[str, Any]] = []
            for link in links:
                item = _clean_link(link)
                if item:
                    out.append(dict(item))
            return out or self._strip_lang_markers(text) or None

        # pojedynczy link, ale tekst bywa "A, B and C"
        parts = [p.strip() for p in re.split(r"\s*(?:,|&| and )\s*", text) if p.strip()]

        def _entity_for_part(part: str) -> Dict[str, Any]:
            # najpierw spróbuj dopasować link do konkretnej części tekstu
            matched_link = self._find_link(part, links)
            if matched_link:
                cleaned = _clean_link(matched_link)
                if cleaned:
                    entity_dict = dict(cleaned)
                    entity_dict["text"] = part
                    return entity_dict
            # jak nie ma linku / został odrzucony – zwróć sam tekst
            return {"text": part, "url": None}

        if len(parts) > 1:
            return [_entity_for_part(p) for p in parts]

        # jeden link, jedna część tekstu
        if links:
            single = _clean_link(links[0])
            if single:
                result = dict(single)
                # tekst z _get_text (bez [it])
                result["text"] = text
                return result

        # brak linków – zwracamy sam tekst
        return text or None

    def _parse_website(self, row: Optional[Dict[str, Any]]) -> Optional[str]:
        if not row:
            return None
        text = (self._get_text(row) or "").strip()
        links = row.get("links") or []
        if links:
            return links[0].get("url") or text or None
        return text or None
