# Amazon Laptop Scraper

A Python scraper practice project for collecting product data from Amazon using `playwright` and `BrightData Scraping Browser` for bot detection bypass.

## Goal

The goal of this project is to practice a pagination-based scraping workflow:

1. Connect to BrightData Scraping Browser via Chrome DevTools Protocol (CDP)
2. Navigate to Amazon.com and search for a product category
3. Extract product details from search results
4. Click the "Next" button to load subsequent result pages
5. Detect when no more pages are available
6. Collect all product data with deduplication
7. Save scraped data to CSV files per category

## Search Categories

The scraper collects products across different search categories:

- laptop

## Data Extracted

The scraper collects detailed information for each product:

- Product Title
- Price
- Customer Rating
- Product URL
