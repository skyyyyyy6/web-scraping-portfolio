# Books Scraper

A Python scraper practice project for collecting book data from Books to Scrape using `requests`, `BeautifulSoup`, JSON writing, request headers, and progress tracking with `tqdm`.

## Goal

The goal of this project is to practice a more complete scraping workflow:

1. Open the Books to Scrape catalogue pages
2. Extract all book links from each page
3. Visit each individual book page
4. Extract detailed book information
5. Save scraped data to a JSON file
6. Handle missing descriptions safely
7. Practice cleaner scraping structure and progress tracking

## Data Extracted

The scraper collects detailed information for each book:

- Book title
- Price (GBP)
- Rating
- Stock availability
- Short description
- Product page link