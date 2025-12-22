import re
from typing import Any, Dict, List, Optional, Union

from models.records import LinkRecord
from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.base.helpers.wiki import clean_link_record
from scrapers.circuits.infobox.services.text_processing import CircuitTextProcessing


class CircuitEntityParser(CircuitTextProcessing):
    """Parsowanie linkowanych encji (architect, owner, website itp.)."""

    _ENTITY_PARTS_RE = re.compile(r"\s*(?:,|&|\band\b)\s*", flags=re.IGNORECASE)

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
                item = clean_link_record(link)
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
                    cleaned = clean_link_record(matched_link)
                    if cleaned:
                        entity_dict = dict(cleaned)
                        entity_dict["text"] = part
                        entities.append(entity_dict)
                        continue
                entities.append({"text": part, "url": None})
            return entities

        single = clean_link_record(links[0])
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

        text = (clean_infobox_text(row.get("text")) or "").strip()
        if not text:
            return None

        links = row.get("links") or []
        parts = self._split_entity_parts(text)
        return self._build_entity_from_links(parts, links)

    def _parse_website(self, row: Optional[Dict[str, Any]]) -> Optional[str]:
        if not row:
            return None
        text = (clean_infobox_text(row.get("text")) or "").strip()
        links = row.get("links") or []
        if links:
            return links[0].get("url") or text or None
        return text or None
