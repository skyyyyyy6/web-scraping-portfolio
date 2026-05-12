# World Population Scraper

A Python scraper practice project for collecting historical population data from Worldometer using `requests`, `BeautifulSoup`, CSV writing, and basic data cleaning with `pandas`.

## Goal

The goal of this project is to practice a more complete scraping workflow:

1. Open the Worldometer population by country page
2. Extract all country profile links
3. Visit each country page
4. Extract population history data for selected years
5. Save raw scraped data to a CSV file
6. Clean the data using pandas
7. Save the cleaned result to a separate CSV file

## Data Extracted

The scraper collects selected population history data for each country:

- Country name
- Year
- Population
- Rank

Selected years:

```txt
2000, 2005, 2010, 2015, 2020, 2022, 2023, 2024, 2025, 2026