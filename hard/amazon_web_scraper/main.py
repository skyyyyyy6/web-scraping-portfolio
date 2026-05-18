import asyncio
import csv
import os
from pathlib import Path
from dotenv import load_dotenv
from playwright.async_api import async_playwright

root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / ".env")

BRIGHTDATA_WEBSOCKET = os.getenv("BRIGHTDATA_WEBSOCKET")
OUTPUT_DIR = "output"
TARGET_PRODUCTS = 500
SEARCH_CATEGORIES = ["laptop"]
PAGE_LOAD_TIMEOUT = 60_000

async def extract_cards(page):
    return await page.evaluate("""
        () => {
            const results = [];
            const seen = new Set();

            document
                .querySelectorAll(".s-card-container")
                .forEach((card) => {
                    const title = card.querySelector("h2 span");
                    const price = card.querySelector("span.a-offscreen");
                    const rating = card.querySelector("span.a-size-small.a-color-base");
                    const href = card.querySelector("a")?.getAttribute("href") || "";
                    
                    let url;
                    if (href.startsWith("http")){
                        url = href;
                    }
                    else{
                        url = "https://www.amazon.com" + href;
                    }

                    if (!title || !price) return;
                    if (!url.startsWith("https://www.amazon.com/") || seen.has(url)) return;

                    seen.add(url);
                    results.push({
                        title: title?.innerText || "",
                        price: price?.innerText || "",
                        rating: rating?.innerText || "",
                        url: url
                    });
                });
            return results;
        }
    """)

async def scrape_category(page, category, target=TARGET_PRODUCTS):
    print(f"Scraping category: {category}")
    all_products = []
    seen_urls = set()
    page_num = 1

    try:
        await page.goto("https://www.amazon.com", wait_until="domcontentloaded", timeout=PAGE_LOAD_TIMEOUT)

        await page.wait_for_selector("#twotabsearchtextbox", timeout=PAGE_LOAD_TIMEOUT)
        await page.type("#twotabsearchtextbox", category)
        await page.keyboard.press("Enter")
        await page.wait_for_selector(".s-card-container", timeout=PAGE_LOAD_TIMEOUT)

        while len(all_products) < target:
            cards = await extract_cards(page)

            for card in cards:
                if card["url"] not in seen_urls:
                    seen_urls.add(card["url"])
                    all_products.append(card)

            print(f"{category}: {len(all_products)}/{target}")

            if len(all_products) >= target:
                break

            next_btn = await page.query_selector("a.s-pagination-next:not(.s-pagination-disabled)")
            if not next_btn:
                print(f"No more pages for '{category}'")
                break

            await next_btn.click()
            await page.wait_for_selector(".s-card-container", timeout=PAGE_LOAD_TIMEOUT)
            await asyncio.sleep(2)
            page_num += 1

        result = all_products[:target]
        print(f"Finished scraping '{category}'. Total products: {len(result)}")
        return result

    except Exception as e:
        print(f"ERROR scraping '{category}': {e}")
        return all_products

def write_csv(rows, filepath):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        field_names = ["title", "price", "rating", "url"]
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(rows)

async def main():
    if not BRIGHTDATA_WEBSOCKET:
        print("ERROR: BRIGHTDATA_WEBSOCKET not found in .env file")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(BRIGHTDATA_WEBSOCKET)
        context = await browser.new_context()
        page = await context.new_page()

        for category in SEARCH_CATEGORIES:
            cards = await scrape_category(page, category)
            category_csv = os.path.join(OUTPUT_DIR, f"{category}.csv")
            
            if cards:
                write_csv(cards, category_csv)
                
                print(f"Saved {len(cards)} rows to {category_csv}")
            else:
                print(f"No products extracted to '{category_csv}'")

        await page.close()
        await context.close()
        await browser.close()

    print(f"Output folder: {os.path.abspath(OUTPUT_DIR)}")

if __name__ == "__main__":
    asyncio.run(main())
