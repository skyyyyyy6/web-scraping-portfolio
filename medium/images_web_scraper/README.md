# Unsplash Images Scraper

A Python scraper practice project for collecting travel image data from Unsplash using `playwright` and `fake-useragent`.

## Goal

The goal of this project is to practice a scroll-based scraping workflow:

1. Open Unsplash search results for a given category
2. Click the "Load more" button to activate infinite scroll
3. Simulate scrolling to trigger dynamic image loading
4. Detect when new images stop loading
5. Extract all image data from the loaded page
6. Save scraped data to CSV files per category and a combined CSV

## Categories

The scraper collects images across 10 travel-related categories:

- travel
- beach
- mountain
- city
- forest
- desert
- island
- road-trip
- architecture
- landscape

## Data Extracted

The scraper collects detailed information for each image:

- Image ID
- Photographer name
- Image URL
- Alt text
- Category
