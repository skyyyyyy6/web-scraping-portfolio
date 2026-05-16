import asyncio
import csv
import os
import re
from urllib.parse import quote

from fake_useragent import UserAgent
from playwright.async_api import async_playwright

IMAGES_PER_CATEGORY = 1000
OUTPUT_DIR = "output"
SCROLL_DELAY_MS = 1400
PAGE_LOAD_TIMEOUT = 30_000

ua = UserAgent()

TRAVEL_CATEGORIES = [
    "travel",
    "beach",
    "mountain",
    "city",
    "forest",
    "desert",
    "island",
    "road-trip",
    "architecture",
    "landscape",
]

async def sleep_ms(ms):
    await asyncio.sleep(ms / 1000)


def extract_photo_id(href):
    match = re.search(r"-([A-Za-z0-9_]{10,12})(?:[?#].*)?$", href)
    if match:
        return match.group(1)

    parts = []
    for part in href.split("/"):
        if part:
            parts.append(part)

    if parts:
        return parts[-1]
    else:
        return ""
    
async def extract_cards(page):
    return await page.evaluate("""
        () => {
            const cards = [];
            
            document
                .querySelectorAll("figure[data-testid='asset-grid-masonry-figure']")
                .forEach((card) => {
                    const link = card.querySelector("a[itemprop='contentUrl']")
                    const image = card.querySelector("img[data-testid='asset-grid-masonry-img']")
                    const credit = card.querySelector("meta[itemprop='creditText']")
                    
                    if (!link || !image) return;
                    
                    cards.push({
                        href: link.getAttribute("href"),
                        imageUrl: image.src,
                        altText: image.alt || "",
                        photographerName: credit?.getAttribute("content") || "",
                    });
                });
            return cards;
        }
    """)
    
    
async def scrape_category(browser, category, target):
    print(f"Scraping category: {category}")
    
    context = await browser.new_context(
        user_agent=ua.random,
        viewport={"width": 1440, "height": 900},
        locale="en-US",
        extra_http_headers={"Accept-Language": "en-US,en;q=0.9"}, 
    )
    page = await context.new_page()
    url = f"https://unsplash.com/s/photos/{quote(category)}"
    images = {}
    
    try:
        await page.goto(url, wait_until="networkidle", timeout=PAGE_LOAD_TIMEOUT)
        
        #getting the "load more" button to start the infinite scroll
        load_more_button = await page.query_selector("button.loadMoreButton-FHXj5M")
        if load_more_button:
            await load_more_button.click()
            await sleep_ms(1000)        
            
        stale_rounds = 0 #counter, how many scrolls with no new images
        last_count = 0 #track number of images from last iteration
        
        while len(images) < target:
            cards = await extract_cards(page)
            
            for card in cards:
                photo_id = extract_photo_id(card["href"])
                
                if photo_id and photo_id not in images:
                    images[photo_id] = {
                        "imageId": photo_id,
                        "photographerName": card["photographerName"],
                        "imageUrl": card["imageUrl"],
                        "altText": card["altText"],
                        "category": category,
                    }
            print(f"{category}: {min(len(images), target)}/{target}")
            
            if(len(images) >= target):
                break
            
            if(len(images) == last_count):
                stale_rounds += 1
                if(stale_rounds >= 6):
                    print(f"No new images found. Stopping at {len(images)} images.")
                    break
            else:
                stale_rounds = 0
            
            last_count = len(images)
            
            await page.evaluate("window.scrollBy(0,window.innerHeight * 3)")
            await sleep_ms(SCROLL_DELAY_MS) #wait 1.4 seconds to load new images
            
        return list(images.values())[:target]
            
    finally:
        await page.close()
        await context.close()

def write_csv(rows, filepath, append = False):
    if append:
        mode = "a"
    else:
        mode = "w"

    with open(filepath, mode, newline="", encoding="utf-8") as csvfile:
        field_names = ["imageId", "photographerName", "imageUrl", "altText", "category",]
        writer = csv.DictWriter(csvfile, fieldnames=field_names)

        if not append:
            writer.writeheader()

        writer.writerows(rows)

async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    combined_csv = os.path.join(OUTPUT_DIR, "unsplash_images_all.csv")
    write_csv([], combined_csv)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        for category in TRAVEL_CATEGORIES:
            rows = await scrape_category(
                browser=browser,
                category=category,
                target=IMAGES_PER_CATEGORY,
            )
            category_csv = os.path.join(OUTPUT_DIR, f"{category}.csv")
            write_csv(rows, category_csv)
            write_csv(rows, combined_csv, append=True)
            
            print(f"Saved {len(rows)} rows to {category_csv}")
            
        await browser.close()
        
    print(f"Output folder: {os.path.abspath(OUTPUT_DIR)}")


if __name__ == "__main__":
    asyncio.run(main())