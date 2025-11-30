from table_scraper import TableScraper

url = "https://en.wikipedia.org/w/api.php"
title = "List of Formula One constructors"
file = "current_constructors"

params = {
    "action": "parse",
    "page": title,
    "format": "json",
    "prop": "text",
    "formatversion": "2",
}

headers = {"User-Agent": "F1Bot/1.0 (bartosz.gembalczyk.stud@pw.edu.pl)"}

scraper = TableScraper(
    url=url,
    params=params,
    headers=headers,
    table_classes=["wikitable", "sortable"],
)

scraper.scrape(f"data/wiki/{file}.csv")
