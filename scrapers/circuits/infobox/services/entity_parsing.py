from typing import Any

from models.records.link import LinkRecord
from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.base.helpers.wiki import clean_link_record
from scrapers.circuits.infobox.services.constants import ENTITY_PARTS_RE
from scrapers.circuits.infobox.services.text_processing import CircuitTextProcessing


class CircuitEntityParser(CircuitTextProcessing):
    """Parsowanie linkowanych encji (architect, owner, website itp.)."""

    def _split_entity_parts(self, text: str) -> list[str]:
        if not text:
            return []
        parts = [part.strip() for part in ENTITY_PARTS_RE.split(text)]
        return [part for part in parts if part]

    def _links_to_entities(self, links: list[LinkRecord]) -> list[dict[str, Any]]:
        entities: list[dict[str, Any]] = []
        for link in links:
            item = clean_link_record(link)
            if item:
                entities.append(dict(item))
        return entities

    def _parts_to_entities(
        self,
        parts: list[str],
        links: list[LinkRecord],
    ) -> list[dict[str, Any]]:
        entities: list[dict[str, Any]] = []
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

    def _build_entity_from_links(
        self,
        parts: list[str],
        links: list[LinkRecord],
    ) -> list[dict[str, Any]] | dict[str, Any] | str | None:
        if len(links) > 1:
            return self._build_from_multiple_links(parts, links)

        if not links:
            return self._build_without_links(parts)

        return self._build_from_single_link(parts, links[0])

    def _build_from_multiple_links(
        self,
        parts: list[str],
        links: list[LinkRecord],
    ) -> list[dict[str, Any]] | str | None:
        entities = self._links_to_entities(links)
        if entities:
            return entities
        fallback = self._strip_lang_markers(", ".join(parts))
        return fallback or None

    @staticmethod
    def _build_without_links(parts: list[str]) -> list[dict[str, Any]] | str | None:
        if len(parts) > 1:
            return [{"text": part, "url": None} for part in parts]
        return parts[0] if parts else None

    def _build_from_single_link(
        self,
        parts: list[str],
        link: LinkRecord,
    ) -> list[dict[str, Any]] | dict[str, Any] | str | None:
        if len(parts) > 1:
            return self._parts_to_entities(parts, [link])

        single = clean_link_record(link)
        if single:
            result = dict(single)
            if parts:
                result["text"] = parts[0]
            return result

        return parts[0] if parts else None

    def parse_linked_entity(
        self,
        row: dict[str, Any] | None,
    ) -> dict[str, Any] | str | list[dict[str, Any]] | None:
        if not row:
            return None

        text = (clean_infobox_text(row.get("text")) or "").strip()
        if not text:
            return None

        links = row.get("links") or []
        parts = self._split_entity_parts(text)
        return self._build_entity_from_links(parts, links)

    @staticmethod
    def _parse_website(row: dict[str, Any] | None) -> str | None:
        if not row:
            return None
        text = (clean_infobox_text(row.get("text")) or "").strip()
        links = row.get("links") or []
        if links:
            return links[0].get("url") or text or None
        return text or None
