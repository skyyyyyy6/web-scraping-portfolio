from fake_useragent import UserAgent
import requests
from bs4 import BeautifulSoup
import json
import time
from tqdm import tqdm

BASE_URL = "https://books.toscrape.com"
RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

ua = UserAgent()

def get_headers():
    return {
        "User-Agent": ua.random,
        "Accept-Language": "en-US,en;q=0.9",
    }

def limit_words(text, max_words=25):

    words = text.split()

    if len(words) <= max_words:

        return text

    return " ".join(words[:max_words]) + "..."

def scrape_listing_page(page_num):
    url = f"{BASE_URL}/catalogue/page-{page_num}.html"
    response = requests.get(url, headers=get_headers(), timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    books = soup.find("ol", class_="row").find_all("article", class_="product_pod")

    results = []
    for book in tqdm(books, desc=f"Scraping", leave=False, ncols=40, bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}"):
        a_tag = book.find("h3").find("a")

        name = a_tag["title"]
        price = book.find("p", class_="price_color").get_text(strip=True).replace("Â£", "£")
        rating_class = book.find("p", class_="star-rating")["class"]
        for word in rating_class:
            if word != "star-rating":
                rating_word = word
                break
        rating = RATING_MAP.get(rating_word, 0)

        link = f"{BASE_URL}/catalogue/{a_tag['href']}"

        avail = book.find("p", class_="availability").get_text(strip=True)

        book_detail_page = requests.get(link, headers=get_headers(), timeout=10)
        book_detail_page.raise_for_status()
        book_detail_soup = BeautifulSoup(book_detail_page.text, "lxml") 
        description_header = book_detail_soup.find("div", id="product_description")
        if description_header:
            description = description_header.find_next_sibling("p").get_text(strip=True)
            description = limit_words(description, 25)
        else:
            description = "No description available"

        time.sleep(0.5)

        results.append({
            "name": name,
            "price_gbp": price,
            "rating": rating,
            "in_stock": avail,
            "description": description,   
            "link": link,
        })
    return results

def main():
    all_books = []
    total_pages = 2

    for page in range(1, total_pages + 1):
        print(f"Scraping page {page}/{total_pages}...", flush=True)
        try:
            books = scrape_listing_page(page)
            all_books.extend(books)
            print(f"{len(books)} books collected (total: {len(all_books)}) | Page {page}", flush=True)
        except Exception as e:
            print(f"ERROR on page {page}: {e}")

        if page < total_pages:
            time.sleep(2)

    OUTPUT_FILE = "books_toscrape.json"
    with open(OUTPUT_FILE, "w", encoding="utf-8") as jsonfile:
        json.dump({"Total": len(all_books), "Books": all_books}, jsonfile, indent=2, ensure_ascii=False)

    print(f"\nScraped {len(all_books)} books in {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
