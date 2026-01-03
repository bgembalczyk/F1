import re
from typing import Any
from typing import Optional

from bs4 import BeautifulSoup
from bs4 import Tag

from models.records.link import LinkRecord
from models.services.rounds_service import RoundsService
from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.parsing import parse_float_from_text
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.helpers.wiki import is_reference_link
from scrapers.base.helpers.text import strip_marks
from scrapers.base.table.columns.constants import FRACTION_RE
from scrapers.base.table.columns.constants import MARKS_RE
from scrapers.base.table.columns.constants import SPLIT_RESULTS_RE
from scrapers.base.table.columns.context import ColumnContext


def split_cell_on_br(cell: Tag) -> list[Tag]:
    html = cell.decode_contents()
    frag_soup = BeautifulSoup(html, "html.parser")
    segments: list[list[Tag]] = [[]]

    for node in list(frag_soup.contents):
        if isinstance(node, Tag) and node.name == "br":
            if segments[-1]:
                segments.append([])
            continue
        segments[-1].append(node)

    wrapped: list[Tag] = []
    for segment in segments:
        if not segment:
            continue
        span = frag_soup.new_tag("span")
        for el in segment:
            span.append(el)
        wrapped.append(span)

    return wrapped or [cell]


def split_engine_cell_on_br(cell: Tag) -> list[Tag]:
    html = replace_link_breaks(cell)
    parts = re.split(r"<br\s*/?>", html, flags=re.IGNORECASE)
    segments: list[Tag] = []
    soup = cell.soup or BeautifulSoup("", "html.parser")

    for part in parts:
        if not part.strip():
            continue
        frag_soup = BeautifulSoup(part, "html.parser")
        span = soup.new_tag("span")
        for el in list(frag_soup.contents):
            span.append(el)
        segments.append(span)

    return segments or [cell]


def split_entrant_cell_on_br(cell: Tag) -> list[Tag]:
    parts: list[str] = []
    current: list[str] = []

    for child in list(cell.contents):
        if isinstance(child, Tag) and child.name and child.name.lower() == "br":
            if current:
                parts.append("".join(current))
                current = []
            continue
        current.append(str(child))

    if current:
        parts.append("".join(current))

    if not parts:
        html = cell.decode_contents()
        parts = re.split(r"<br\\s*/?>", html, flags=re.IGNORECASE)
    segments: list[Tag] = []
    soup = cell.soup or BeautifulSoup("", "html.parser")

    for part in parts:
        if not part.strip():
            continue
        frag_soup = BeautifulSoup(part, "html.parser")
        span = soup.new_tag("span")
        for el in list(frag_soup.contents):
            span.append(el)
        segments.append(span)

    return segments or [cell]


def extract_layout_text(clean_text: str, link_text: str) -> Optional[str]:
    if not clean_text:
        return None

    if link_text:
        lower_clean = clean_text.lower()
        lower_link = link_text.lower()
        idx = lower_clean.find(lower_link)
        if idx != -1:
            clean_text = (clean_text[:idx] + clean_text[idx + len(link_text) :]).strip()

    clean_text = clean_text.strip(" -–—()")
    if not clean_text:
        return None

    if link_text and clean_text.lower() == link_text.lower():
        return None

    return clean_text


def split_constructor_lines(ctx: ColumnContext) -> list[ColumnContext]:
    if not ctx.cell:
        return []

    lines: list[list[object]] = [[]]
    for child in ctx.cell.children:
        if isinstance(child, Tag) and child.name == "br":
            lines.append([])
            continue
        lines[-1].append(child)

    if not lines:
        return []

    line_link_counts = []
    for line in lines:
        link_count = 0
        for node in line:
            if isinstance(node, Tag):
                if node.name == "a":
                    link_count += 1
                else:
                    link_count += len(node.find_all("a"))
        line_link_counts.append(link_count)

    line_contexts: list[ColumnContext] = []
    link_index = 0
    for line, link_count in zip(lines, line_link_counts):
        line_links = ctx.links[link_index : link_index + link_count]
        link_index += link_count

        text_parts = []
        for node in line:
            if isinstance(node, Tag):
                node_text = node.get_text(" ", strip=True)
            else:
                node_text = str(node).strip()
            if node_text:
                text_parts.append(node_text)
        line_text = " ".join(text_parts).strip()
        clean_text = clean_wiki_text(line_text)

        if not clean_text and not line_links:
            continue

        line_contexts.append(
            ColumnContext(
                header=ctx.header,
                key=ctx.key,
                raw_text=line_text,
                clean_text=clean_text,
                links=line_links,
                cell=None,
                skip_sentinel=ctx.skip_sentinel,
                model_fields=ctx.model_fields,
                header_link=ctx.header_link,
            )
        )

    return line_contexts


def extract_constructor_part(ctx, index: int) -> LinkRecord | None:
    links = normalize_links(ctx.links, strip_marks=True, drop_empty=True)
    clean_text = clean_wiki_text(ctx.clean_text or "")

    split_parts = split_on_external_hyphen(ctx)
    if split_parts:
        left_part, right_part = split_parts
        if links:
            if index == 0:
                left_normalized = clean_wiki_text(left_part)
                for link in links:
                    if clean_wiki_text(link.get("text", "")) == left_normalized:
                        return link
                return {"text": left_part, "url": None}
            right_normalized = clean_wiki_text(right_part)
            for link in links:
                if clean_wiki_text(link.get("text", "")) == right_normalized:
                    return link
            return {"text": right_part, "url": None}
        return {"text": left_part if index == 0 else right_part, "url": None}

    if links:
        if len(links) >= 2:
            return links[index] if index < len(links) else None
        return links[0]

    if not clean_text:
        return None

    return {"text": clean_text, "url": None}


def split_on_external_hyphen(ctx) -> tuple[str, str] | None:
    raw_text = clean_wiki_text(ctx.raw_text or "", normalize_dashes=False)
    match = re.search(r"\s[-–—−]\s", raw_text)
    if not match:
        return None
    left_part = raw_text[: match.start()].strip()
    right_part = raw_text[match.end() :].strip()
    if not left_part or not right_part:
        return None
    return left_part, right_part


def build_driver_link_lookup(links: list[dict[str, str | None]]):
    lookup: dict[str, list[dict[str, str | None]]] = {}
    for link in normalize_links(links, strip_marks=True, drop_empty=True):
        text = link.get("text") or ""
        if not text:
            continue
        lookup.setdefault(text, []).append(link)
    return lookup


def parse_driver_segment(
    segment: Tag,
    link_lookup: dict[str, list[dict[str, str | None]]],
    *,
    total_rounds: int | None,
) -> dict[str, Any] | None:
    clean_text = clean_wiki_text(segment.get_text(" ", strip=True))
    if not clean_text:
        return None

    rounds_text = extract_rounds_text(clean_text)
    rounds = (
        RoundsService.parse_rounds(rounds_text, total_rounds=total_rounds)
        if rounds_text
        else []
    )
    number = extract_number(clean_text)

    driver = extract_driver(segment, link_lookup, clean_text)
    if not driver:
        return None

    record: dict[str, Any] = {"driver": driver}
    if number is not None:
        record["no"] = number
    if rounds_text or rounds:
        record["rounds"] = rounds
    return record


def extract_driver(
    segment: Tag,
    link_lookup: dict[str, list[dict[str, str | None]]],
    clean_text: str,
) -> dict[str, str | None] | None:
    for a in segment.find_all("a", href=True):
        text = clean_wiki_text(a.get_text(strip=True))
        if not text:
            continue
        candidates = link_lookup.get(text)
        if candidates:
            return candidates[0]
        return {"text": text, "url": None}

    cleaned = strip_rounds_and_number(clean_text)
    if cleaned:
        return {"text": cleaned, "url": None}
    return None


def extract_rounds_text(text: str) -> str | None:
    match = re.search(r"\\(([^)]+)\\)", text)
    if match:
        return match.group(1).strip()

    match = re.search(r"Rounds?\\s*:?\\s*(.+)$", text, re.I)
    if match:
        return match.group(1).strip()

    return None


def extract_number(text: str) -> int | None:
    match = re.match(r"^\\s*(\\d+)\\b", text)
    if match:
        return int(match.group(1))

    match = re.search(r"\\bNo\\.?\\s*(\\d+)\\b", text, re.I)
    if match:
        return int(match.group(1))

    return None


def strip_rounds_and_number(text: str) -> str:
    cleaned = re.sub(r"\\(([^)]+)\\)", "", text)
    cleaned = re.sub(r"^\\s*\\d+\\b", "", cleaned)
    cleaned = re.sub(r"\\bNo\\.?\\s*\\d+\\b", "", cleaned, flags=re.I)
    cleaned = re.sub(r"Rounds?\\s*:?\\s*.+$", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\\s+", " ", cleaned).strip(" -–—")
    return cleaned.strip()


def extract_engine_class(cell: Tag) -> str | None:
    background = extract_background(cell)
    if not background:
        return None
    if is_f2_background(background):
        return "F2"
    return None


def extract_background(cell: Tag) -> str | None:
    style = cell.get("style") or ""
    if style:
        match = re.search(r"background(?:-color)?\s*:\s*([^;]+)", style, re.I)
        if match:
            return match.group(1).strip()

    bgcolor = cell.get("bgcolor")
    if bgcolor:
        return str(bgcolor).strip()

    return None


def is_f2_background(background: str) -> bool:
    match = re.search(r"#?([0-9a-f]{6}|[0-9a-f]{3})", background, re.I)
    if not match:
        return False
    value = match.group(1).lower()
    if len(value) == 3:
        value = "".join(char * 2 for char in value)
    return value == "ffcccc"


def replace_link_breaks(cell: Tag) -> str:
    fragment = BeautifulSoup(cell.decode_contents(), "html.parser")
    for br in fragment.find_all("br"):
        if br.find_parent("a"):
            br.replace_with(" ")
    return str(fragment)


def build_engine_link_lookup(links: list[LinkRecord]) -> dict[str, list[LinkRecord]]:
    lookup: dict[str, list[LinkRecord]] = {}
    for link in normalize_links(links, strip_marks=True, drop_empty=True):
        text = link.get("text") or ""
        if not text:
            continue
        lookup.setdefault(text, []).append(link)
    return lookup


def parse_engine_segment(
    segment: Tag, link_lookup: dict[str, list[LinkRecord]]
) -> dict[str, Any] | None:
    raw_links: list[LinkRecord] = []
    for a in segment.find_all("a", href=True):
        text = clean_wiki_text(a.get_text(strip=True))
        if not text:
            continue
        candidates = link_lookup.get(text)
        if candidates:
            raw_links.append(candidates[0])
        else:
            raw_links.append({"text": text, "url": None})

    links = normalize_links(raw_links, strip_marks=True, drop_empty=True)
    clean_text = clean_wiki_text(segment.get_text(" ", strip=True))
    if not links and not clean_text:
        return None

    model: LinkRecord | None = links[0] if links else None

    displacement = extract_displacement(clean_text)
    type_text = extract_type_text(clean_text, displacement)
    supercharged = extract_supercharged(clean_text)
    turbocharged = extract_turbocharged(clean_text)
    gas_turbine = extract_gas_turbine(clean_text)
    layout, cylinders = parse_engine_type(type_text)
    model_text = extract_model_text(
        clean_text,
        type_text=type_text,
        supercharged=supercharged,
        turbocharged=turbocharged,
        gas_turbine=gas_turbine,
        displacement=displacement,
    )
    if model and model_text:
        model = {**model, "text": model_text}

    data: dict[str, Any] = {}
    if model:
        data["model"] = model
    if displacement:
        data["displacement_l"] = displacement
    if type_text:
        data["type"] = type_text
    if layout:
        data["layout"] = layout
    if cylinders is not None:
        data["cylinders"] = cylinders
    if supercharged:
        data["supercharged"] = True
    if turbocharged:
        data["turbocharged"] = True
    if gas_turbine:
        data["gas_turbine"] = True
    return data or None


def extract_displacement(text: str) -> float | None:
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:L|litre|liter)s?\b", text, re.I)
    if not match:
        match = re.search(r"\b(\d+(?:\.\d+))\b", text)
        if not match:
            return None
    try:
        value = float(match.group(1))
        if value <= 0 or value > 10:
            return None
        return value
    except ValueError:
        return None


def extract_type_text(text: str, displacement: float | None) -> str | None:
    if not text:
        return None
    cleaned = text
    cleaned = re.sub(
        r"(\d+(?:\.\d+)?)\s*(?:L|litre|liter)s?\b", "", cleaned, flags=re.I
    )
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    match = re.search(
        r"\b(?:V\d{1,2}|W\d{1,2}|I\d{1,2}|L\d{1,2}|H\d{1,2}|F(?:4|6|8|10|12)|Flat[-\s]?\d{1,2}|Straight[-\s]?\d{1,2}|Inline[-\s]?\d{1,2})\b",
        cleaned,
        re.I,
    )
    if match:
        raw = match.group(0)
        normalized = raw.replace(" ", "").replace("-", "")
        lowered = normalized.lower()
        if lowered.startswith(("straight", "inline")):
            digits = re.search(r"\d{1,2}", normalized)
            if digits:
                return f"L{digits.group(0)}"
        return normalized

    if displacement is None:
        match = re.search(r"\bV\d{1,2}\b", text, re.I)
        if match:
            return match.group(0)

    return None


def parse_engine_type(type_text: str | None) -> tuple[str | None, int | None]:
    if not type_text:
        return None, None
    normalized = type_text.replace(" ", "").replace("-", "")
    match = re.match(r"([A-Za-z]+)(\d{1,2})$", normalized)
    if not match:
        return None, None
    layout = match.group(1).upper()
    if layout in {"STRAIGHT", "INLINE", "I", "L"}:
        layout = "L"
    try:
        cylinders = int(match.group(2))
    except ValueError:
        cylinders = None
    return layout, cylinders


def extract_supercharged(text: str) -> bool | None:
    if not text:
        return None
    if re.search(r"\b(supercharger|supercharged)\b", text, re.I):
        return True
    stripped = text.strip()
    if re.search(r"(?:^|\s)s$", stripped, re.I):
        return True
    return None


def extract_turbocharged(text: str) -> bool | None:
    if not text:
        return None
    if re.search(r"\b(turbo|turbocharged)\b", text, re.I):
        return True
    stripped = text.strip()
    if re.search(r"(?:^|\s)t$", stripped, re.I):
        return True
    return None


def extract_gas_turbine(text: str) -> bool | None:
    if not text:
        return None
    if re.search(r"\b(gas\s*turbine|turbine)\b", text, re.I):
        return True
    stripped = text.strip()
    if re.search(r"(?:^|\s)tbn$", stripped, re.I):
        return True
    return None


def extract_model_text(
    text: str,
    *,
    type_text: str | None,
    supercharged: bool | None,
    turbocharged: bool | None,
    gas_turbine: bool | None,
    displacement: float | None,
) -> str | None:
    if not text:
        return None
    cleaned = text
    cleaned = re.sub(
        r"(\d+(?:\.\d+)?)\s*(?:L|litre|liter)s?\b", "", cleaned, flags=re.I
    )
    cleaned = re.sub(
        r"\b(?:V\d{1,2}|W\d{1,2}|I\d{1,2}|L\d{1,2}|H\d{1,2}|F(?:4|6|8|10|12)|Flat[-\s]?\d{1,2}|Straight[-\s]?\d{1,2}|Inline[-\s]?\d{1,2})\b",
        "",
        cleaned,
        flags=re.I,
    )
    if type_text:
        normalized_type = re.escape(type_text)
        cleaned = re.sub(normalized_type, "", cleaned, flags=re.I)
    if supercharged:
        cleaned = re.sub(r"\b(supercharger|supercharged)\b", "", cleaned, flags=re.I)
        cleaned = re.sub(r"(?:^|\s)s$", "", cleaned, flags=re.I)
    if turbocharged:
        cleaned = re.sub(r"\b(turbo|turbocharged)\b", "", cleaned, flags=re.I)
        cleaned = re.sub(r"(?:^|\s)t$", "", cleaned, flags=re.I)
    if gas_turbine:
        cleaned = re.sub(r"\b(gas\s*turbine|turbine)\b", "", cleaned, flags=re.I)
        cleaned = re.sub(r"(?:^|\s)tbn$", "", cleaned, flags=re.I)
    if displacement is not None:
        cleaned = re.sub(rf"\b{re.escape(str(displacement))}\b", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or None


def parse_entrant_segment(
    segment: Tag,
    link_lookup: dict[str, list[dict[str, str | None]]],
) -> dict[str, Any] | None:
    license_info = extract_licenses(segment, link_lookup)
    strip_refs(segment)

    name = clean_wiki_text(segment.get_text(" ", strip=True))
    if not name:
        return None

    sponsors: list[dict[str, str | None]] = []
    for a in segment.find_all("a", href=True):
        if is_reference_link(a, allow_local_anchors=True):
            continue
        text = clean_wiki_text(a.get_text(strip=True))
        if not text:
            continue
        candidates = link_lookup.get(text)
        if candidates:
            sponsors.append(candidates[0])
        else:
            sponsors.append({"text": text, "url": None})

    record: dict[str, Any] = {"name": name, "title_sponsors": sponsors}
    if license_info is not None:
        record["license"] = license_info
    return record


def extract_licenses(
    segment: Tag,
    link_lookup: dict[str, list[dict[str, str | None]]],
) -> dict[str, str | None] | None:
    licenses: list[dict[str, str | None]] = []
    for node in segment.select(".flagicon"):
        for a in node.find_all("a", href=True):
            text = clean_wiki_text(a.get_text(strip=True))
            if not text:
                continue
            candidates = link_lookup.get(text)
            if candidates:
                licenses.append(candidates[0])
            else:
                licenses.append({"text": text, "url": a.get("href")})
            break
        node.decompose()

    if not licenses:
        return None

    license_text = " / ".join(link.get("text") or "" for link in licenses).strip()
    license_url = " / ".join(
        link.get("url") or "" for link in licenses if link.get("url") is not None
    ).strip()
    return {
        "text": license_text,
        "url": license_url or None,
    }


def strip_refs(segment: Tag) -> None:
    for sup in segment.find_all("sup", class_="reference"):
        sup.decompose()


def parse_points_value(text: str):
    if not text:
        return None

    match = FRACTION_RE.search(text)
    if match:
        whole = int(match.group(1)) if match.group(1) else 0
        numerator = int(match.group(2))
        denominator = int(match.group(3))
        if denominator == 0:
            return None
        return whole + numerator / denominator

    return parse_float_from_text(text)


def parse_results(text: str) -> list[dict[str, Any]]:
    parts = SPLIT_RESULTS_RE.split(text)
    results: list[dict[str, Any]] = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        marks = MARKS_RE.findall(part)
        cleaned = strip_marks(part) or ""
        cleaned = cleaned.strip()
        value: int | str | None
        if not cleaned or cleaned == "-":
            value = None
        elif cleaned.isdigit():
            value = int(cleaned)
        else:
            value = cleaned
        results.append(
            {
                "value": value,
                "marks": marks or None,
            }
        )
    return results


def parse_superscripts(ctx: ColumnContext) -> tuple[int | None, bool, bool]:
    cell = ctx.cell
    if cell is None:
        return None, False, False

    sup_texts = []
    for sup in cell.find_all("sup"):
        sup_text = clean_wiki_text(sup.get_text(" ", strip=True))
        if sup_text:
            sup_texts.append(sup_text)

    sprint_position = None
    pole_position = False
    fastest_lap = False

    for token in " ".join(sup_texts).split():
        if token.isdigit() and sprint_position is None:
            sprint_position = int(token)
            continue
        letters = re.findall(r"[A-Za-z]", token)
        for letter in letters:
            upper = letter.upper()
            if upper == "P":
                pole_position = True
            elif upper == "F":
                fastest_lap = True

    if not pole_position and cell.find(["b", "strong"]):
        pole_position = True
    if not fastest_lap and cell.find(["i", "em"]):
        fastest_lap = True

    return sprint_position, pole_position, fastest_lap


def extract_race_result_background(ctx: ColumnContext) -> str | None:
    cell = ctx.cell
    if cell is None:
        return None

    style = cell.get("style") or ""
    if style:
        match = re.search(r"background(?:-color)?\s*:\s*([^;]+)", style, re.I)
        if match:
            return match.group(1).strip()

    bgcolor = cell.get("bgcolor")
    if bgcolor:
        return str(bgcolor).strip()

    return None


def has_year(text: str) -> bool:
    return re.search(r"\\b\\d{4}\\b", text) is not None
