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

    _ENTITY_PARTS_RE = re.compile(r"\s*(?:,|&|\band\b)\s*", flags=re.IGNORECASE)

    def _clean_link(self, link_record: LinkRecord) -> Optional[LinkRecord]:
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

    def _split_entity_parts(self, text: str) -> list[str]:
        if not text:
            return []
        parts = [part.strip() for part in self._ENTITY_PARTS_RE.split(text)]
        return [part for part in parts if part]

    def _build_entity_from_links(
        self, parts: list[str], links: list[LinkRecord]
    ) -> Union[List[Dict[str, Any]], Dict[str, Any], str, None]:
        if len(links) > 1:
            out: List[Dict[str, Any]] = []
            for link in links:
                item = self._clean_link(link)
                if item:
                    out.append(dict(item))
            if out:
                return out
            fallback = self._strip_lang_markers(", ".join(parts))
            return fallback or None

        if not links:
            if len(parts) > 1:
                return [{"text": part, "url": None} for part in parts]
            return parts[0] if parts else None

        if len(parts) > 1:
            entities: List[Dict[str, Any]] = []
            for part in parts:
                matched_link = self._find_link(part, links)
                if matched_link:
                    cleaned = self._clean_link(matched_link)
                    if cleaned:
                        entity_dict = dict(cleaned)
                        entity_dict["text"] = part
                        entities.append(entity_dict)
                        continue
                entities.append({"text": part, "url": None})
            return entities

        single = self._clean_link(links[0])
        if single:
            result = dict(single)
            if parts:
                result["text"] = parts[0]
            return result

        return parts[0] if parts else None

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
        parts = self._split_entity_parts(text)
        return self._build_entity_from_links(parts, links)

    def _parse_website(self, row: Optional[Dict[str, Any]]) -> Optional[str]:
        if not row:
            return None
        text = (self._get_text(row) or "").strip()
        links = row.get("links") or []
        if links:
            return links[0].get("url") or text or None
        return text or None
