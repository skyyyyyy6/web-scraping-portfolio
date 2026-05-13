# Quotes Scroll Scraper

A Python scraper practice project for collecting quotes data from Quotes to Scrape (infinite scroll version) using `playwright`, `fake-useragent`, XML writing, and progress tracking with `tqdm`.

## Goal

The goal of this project is to practice a scroll-based scraping workflow:

1. Open the Quotes to Scrape infinite scroll page
2. Simulate mouse scrolling to trigger dynamic quote loading
3. Detect when new quotes stop loading
4. Extract all quote data from the loaded page
5. Save scraped data to an XML file
6. Practice async scraping with Playwright

## Data Extracted

The scraper collects detailed information for each quote:

- Quote description (limited to 15 words)
- Author name
- Associated tags