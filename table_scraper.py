import requests
import csv
from bs4 import BeautifulSoup


class TableScraper:
    def __init__(self, url, params=None, headers=None, table_classes=None):
        self.url = url
        self.params = params or {}
        self.headers = headers or {}
        self.table_classes = table_classes or ["wikitable", "sortable"]

    @staticmethod
    def clean_text(text: str) -> str:
        return (
            text.strip()
            .replace("\n", "")
            .replace("\xa0", "")
            .replace("/", "")
        )

    def fetch_html(self) -> str:
        print("📡 Pobieranie danych z API...")
        response = requests.get(self.url, params=self.params, headers=self.headers)
        response.raise_for_status()

        print("✔️  Odebrano odpowiedź, dekoduję JSON...")
        data = response.json()

        print("✔️  Wyciągam HTML z pola 'parse.text'...")
        return data["parse"]["text"]

    def extract_tables(self, html: str):
        print("🔍 Parsuję HTML BeautifulSoup-em...")
        soup = BeautifulSoup(html, "html.parser")

        tables = soup.find_all("table", class_=self.table_classes)
        print(f"✔️  Znaleziono {len(tables)} tabel(e) pasujące do klas: {self.table_classes}")

        return tables

    def parse_table(self, table):
        print("🧩 Parsuję nagłówki tabeli...")
        headers = [th.get_text(strip=True).rstrip(":") for th in table.find_all("th")]
        print(f"✔️  Nagłówki: {headers}")

        rows = []
        row_count = 0

        print("🛠️  Przetwarzam wiersze...")
        for tr in table.find_all("tr")[1:]:
            row_data = []

            for td in tr.find_all("td"):
                if len(td.contents) <= 2:
                    cell_value = self.clean_text(td.get_text())
                else:
                    texts = []
                    for content in td.contents:
                        if content == "\n":
                            continue
                        try:
                            texts.append(self.clean_text(content.get_text()))
                        except AttributeError:
                            texts.append(self.clean_text(str(content)))
                    cell_value = " ".join(texts)

                row_data.append(cell_value)

            if row_data:
                rows.append(row_data)
                row_count += 1

                # Pokazuj progres co 5 wierszy
                if row_count % 5 == 0:
                    print(f"   → przetworzono {row_count} wierszy...")

        print(f"✔️  Skończono: {row_count} wierszy przetworzonych.")
        return headers, rows

    def save_to_csv(self, filename: str, headers, rows):
        print(f"💾 Zapisuję wyniki do pliku: {filename}")
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

        print("✔️  Zapis CSV zakończony!")

    def scrape(self, output_file: str, table_index: int = 0):
        print("=== 🚀 ROZPOCZYNAM SCRAPOWANIE TABELI ===")

        html = self.fetch_html()
        tables = self.extract_tables(html)

        if not tables:
            raise ValueError("❌ Nie znaleziono żadnych pasujących tabel.")

        print(f"📄 Używam tabeli nr {table_index}...")
        headers, rows = self.parse_table(tables[table_index])

        self.save_to_csv(output_file, headers, rows)

        print("=== 🏁 ZAKOŃCZONO SCRAPOWANIE ===")
        return headers, rows
