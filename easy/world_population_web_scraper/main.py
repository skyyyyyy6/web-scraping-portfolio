import requests
from bs4 import BeautifulSoup
import time
import csv
import pandas as pd
from pathlib import Path
from fake_useragent import UserAgent

ua = UserAgent()

def get_headers():
    return {
        "User-Agent": ua.random,
        "Accept-Language": "en-US,en;q=0.9",
    }

YEARS = [2000, 2005, 2010, 2015, 2020, 2022, 2023, 2024, 2025, 2026]
OUTPUT_CSV  = "world_population_2000_2026.csv"

def get_country_links(session):
    url = "https://www.worldometers.info/world-population/population-by-country/"
    response = session.get(url, headers=get_headers(), timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", class_="datatable")
    rows = table.find("tbody").find_all("tr")

    countries = []
    for row in rows:
        country_name = row.find("a", class_="transition-colors text-primary hover:text-primary/80")
        if not country_name:
            continue
        countries.append({
            "name": country_name.get_text(strip=True),
            "url": "https://www.worldometers.info" + country_name["href"],
        })

    print(f"Found {len(countries)} countries.")
    return countries


def scrape_country_history(session, country):
    response = session.get(country["url"], headers=get_headers(), timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", class_="datatable")

    if not table:
        print(f"No history table found for {country['name']}")
        return []

    rows = table.find("tbody").find_all("tr")

    each_row = []
    for row in rows:
        cols = []
        for td in row.find_all("td"):
            cols.append(td.get_text(strip=True))

        if not cols:
            continue
        try:
            year = int(cols[0])
        except (ValueError, IndexError):
            continue

        if year not in YEARS:
            continue

        if len(cols) > 1:
            population = cols[1].replace(",", "")
        else:
            population = "-"

        if len(cols) > 12:
            rank = cols[12]
        else:
            rank = "-"

        each_row.append({
            "country":    country["name"],
            "year":       year,
            "population": population,
            "rank":       rank,
        })

    return each_row


def scrape(session):
    scraped = set()
    if Path(OUTPUT_CSV).exists():
        existing = pd.read_csv(OUTPUT_CSV)
        scraped = set(existing["country"].unique())
        print(f"Resuming | {len(scraped)} countries already scraped.")

    countries = get_country_links(session)

    write_header = len(scraped) == 0
    with open(OUTPUT_CSV, "a", newline="", encoding="utf-8") as f:
        field_names = ["country", "year", "population", "rank"]
        writer = csv.DictWriter(f, fieldnames=field_names)
        if write_header:
            writer.writeheader()

        for i, country in enumerate(countries, start=1):
            if country["name"] in scraped:
                print(f"[{i}/{len(countries)}] Skipping:  {country['name']}")
                continue

            print(f"[{i}/{len(countries)}] Scraping:  {country['name']}")
            for attempt in range(3):
                try:
                    rows = scrape_country_history(session, country)
                    writer.writerows(rows)
                    f.flush()
                    break
                except requests.RequestException as e:
                    print(f"  [ERROR] attempt {attempt + 1}: {e}")
                    time.sleep(3)

            time.sleep(0.5)

    print(f"\nRaw data saved to: {OUTPUT_CSV}")


def clean_and_export():
    df = pd.read_csv(OUTPUT_CSV)

    df["population"] = pd.to_numeric(df["population"], errors="coerce").astype("Int64")
    df["rank"] = pd.to_numeric(df["rank"], errors="coerce").astype("Int64")
    df["year"] = df["year"].astype(int)

    df = df.sort_values(["year", "rank"], ascending=[False, True]).reset_index(drop=True)
    df.to_csv("world_population_clean.csv", index=False)

    # df.to_json("world_population_clean.json", orient="records", indent=2)

    # df.to_xml("world_population_clean.xml", index=False)

    # with pd.ExcelWriter("world_population_clean.xlsx", engine="openpyxl") as writer:
    #     df.to_excel(writer, index=False, sheet_name="Population")
    #     ws = writer.sheets["Population"]
    #     for row in ws.iter_rows(min_row=2, min_col=3, max_col=3):
    #         for cell in row:
    #             cell.number_format = "#,##0"
    #     for col in ws.columns:
    #         max_len = max(len(str(cell.value or "")) for cell in col)
    #         ws.column_dimensions[col[0].column_letter].width = max_len + 4

    print(f"Clean CSV saved to: world_population_clean.csv")
    print(f"\nShape: {df.shape[0]} rows x {df.shape[1]} columns")
    print(df.head(10).to_string(index=False))

def main():
    with requests.Session() as session:
        scrape(session)
    clean_and_export()


if __name__ == "__main__":
    main()
