import asyncio
import xml.etree.ElementTree as ET
from fake_useragent import UserAgent
from tqdm import tqdm
from playwright.async_api import async_playwright


URL = "https://quotes.toscrape.com/scroll"

MAX_QUOTES = 1000

ua = UserAgent()

# Limit descriptions to 15 words for performance optimization
def limit_words(text, max_words=15):
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "..."

async def scrape_quotes():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent = ua.random,
            extra_http_headers={
                    "Accept-Language": "en-US,en;q=0.9"
                }
            )
        page = await context.new_page()

        await page.goto(URL)
        await page.wait_for_selector(".quote")

        previous_count = 0

        while True:
            await page.mouse.wheel(0, 3000)
            await page.wait_for_timeout(2000)

            current_count = await page.locator(".quote").count()

            if current_count == previous_count:
                print("No new quotes loaded.")
                break

            if current_count >= MAX_QUOTES:
                break

            print(f"Quotes loaded: {current_count}")
            previous_count = current_count

        results = []

        quotes = await page.query_selector_all(".quote")
        quotes = quotes[:MAX_QUOTES]

        for quote in tqdm(quotes, desc="Scraping:", ncols=40, bar_format="{desc} {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}"):
            description = await quote.query_selector("span.text")
            author = await quote.query_selector("small.author")
            tag_element = await quote.query_selector_all("a.tag")

            tags = []
            for tag in tag_element:
                tag_text = await tag.inner_text()
                tags.append(tag_text)

            results.append({
                "description": limit_words(await description.inner_text() if description else ""), 
                "by_who": await author.inner_text() if author else "",
                "tags": tags
            })

        await browser.close()
        return results

def save_to_xml(quotes, output_file="quotes_scroll.xml"):
    root = ET.Element("quotes")

    for item in quotes:
        quote = ET.SubElement(root, "quote")

        description = ET.SubElement(quote, "description")
        description.text = item["description"]

        by_who = ET.SubElement(quote, "by_who")
        by_who.text = item["by_who"]

        tags = ET.SubElement(quote, "tags")
        tags.text = ", ".join(item["tags"])

    tree = ET.ElementTree(root)
    ET.indent(tree, space=" " * 4)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)


async def main():
    quotes = await scrape_quotes()
    save_to_xml(quotes)

    print(f"Total quotes scraped: {len(quotes)}")


if __name__ == "__main__":
    asyncio.run(main())