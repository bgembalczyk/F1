from typing import Optional, List, Dict, Any

from bs4 import BeautifulSoup, Tag  # <-- rozszerzamy o Tag
import re  # <-- nowy

from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.date import DateColumn
from scrapers.base.table.columns.types.driver import DriverColumn
from scrapers.base.table.columns.types.time import TimeColumn
from scrapers.base.table.columns.types.url import UrlColumn
from scrapers.base.table.scraper import F1TableScraper

# NOWE:
from scrapers.base.helpers.utils import clean_wiki_text, extract_links_from_cell
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.registry import resolve_column_type


class LapRecordsTableScraper(F1TableScraper):
    """
    Lekki scraper pojedynczej tabeli z rekordami okrążeń.

    Używany tylko jako helper w F1SingleCircuitScraper – korzystamy z całej
    logiki kolumn / ColumnContext / extract_links_from_cell itd.
    """

    # Nie wiążemy się z żadną konkretną sekcją
    section_id: Optional[str] = None

    # Minimalny zestaw nagłówków, żeby uznać tabelę za „rekordową”.
    # (kolejność nie ma znaczenia)
    expected_headers = [
        "Time",
    ]

    # mapowanie oryginalnych nagłówków → klucze w rekordzie
    column_map = {
        "Category": "category",
        "Class": "class_",
        "Driver": "driver",
        "Driver/Rider": "driver_rider",
        "Vehicle": "vehicle",
        "Event": "event",
        "Time": "time",
        "Date": "date",
    }

    columns = {
        # Tekst + link (jeśli jest)
        "category": AutoColumn(),
        "class_": AutoColumn(),
        "driver": DriverColumn(),
        "driver_rider": DriverColumn(),
        "vehicle": AutoColumn(),
        "event": UrlColumn(),
        # Nowe kolumny – parsują tekst do ustandaryzowanej postaci
        "time": TimeColumn(),
        "date": DateColumn(),
    }

    def _parse_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Nie używamy standardowego fetch()/_parse_soup – w F1SingleCircuitScraper
        sami podajemy konkretne tabele i nagłówki i wołamy parse_row().
        Metoda zostaje tylko po to, żeby klasa była kompletna.
        """
        raise NotImplementedError(
            "_LapRecordsTableScraper nie jest używany bezpośrednio – "
            "korzystaj z parse_row() na konkretnych tabelach."
        )

    def _split_cell_on_br(self, cell: Tag) -> List[Tag]:
        html = cell.decode_contents()
        parts = re.split(r"<br\s*/?>", html, flags=re.IGNORECASE)

        segments: List[Tag] = []
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

    def parse_multi_row(
        self,
        row: Tag,
        cells: List[Tag],
        headers: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Z jednego <tr> zwraca 1..N rekordów.

        Jeśli w którejkolwiek komórce są wartości rozdzielone <br>, traktujemy je
        jako osobne „podwiersze”, np.:

        - Driver:  "Ross Cheever<br>John Bowe"
        - Vehicle: "Ralt RT4<br>Ralt RT4 Cosworth"
        - Time:    "1:33.20"

        → dwa rekordy:
          - [driver=Ross Cheever, vehicle=Ralt RT4,           time=1:33.20]
          - [driver=John Bowe,   vehicle=Ralt RT4 Cosworth,  time=1:33.20]

        Komórki z jedną wartością są duplikowane do wszystkich segmentów.
        """
        # Najpierw dla każdej komórki zbuduj listę segmentów
        per_cell_segments: List[List[Tag]] = []
        max_segments = 1

        for cell in cells:
            segs = self._split_cell_on_br(cell)
            per_cell_segments.append(segs)
            if len(segs) > max_segments:
                max_segments = len(segs)

        model_fields = self._model_fields()
        records: List[Dict[str, Any]] = []

        # Dla każdego segmentu budujemy osobny rekord
        for idx in range(max_segments):
            record: Dict[str, Any] = {}

            for header, cell, segs in zip(headers, cells, per_cell_segments):
                # jeśli komórka ma mniej segmentów, powielamy ostatni
                seg_cell = segs[idx] if idx < len(segs) else segs[-1]

                key = self.column_map.get(header, self._normalize_header(header))

                raw_text = seg_cell.get_text(" ", strip=True)
                clean_text = clean_wiki_text(raw_text)

                links: list[dict[str, Any]] = []
                if self.include_urls:
                    links = extract_links_from_cell(seg_cell, full_url=self._full_url)

                ctx = ColumnContext(
                    header=header,
                    key=key,
                    raw_text=raw_text,
                    clean_text=clean_text,
                    links=links,
                    cell=seg_cell,
                    skip_sentinel=self._SKIP,
                    model_fields=model_fields,
                )

                col_spec = (
                    self.columns.get(key)
                    or self.columns.get(header)
                    or self.default_column
                )
                col = resolve_column_type(col_spec)

                col.apply(ctx, record)

            # Ewentualne mapowanie do modelu, gdyby kiedyś zostało dodane
            if self.model_class:
                model = self.model_class(**record)
                if hasattr(model, "model_dump"):
                    record = model.model_dump()
                elif hasattr(model, "dict"):
                    record = model.dict()
                # dataclass też można obsłużyć, ale tu nie jest używane

            records.append(record)

        return records
