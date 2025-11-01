import requests
import json
import os
import time

# ---------------- CONFIG ----------------
API_KEY = "7a614e465a0a58682bd869ceee1540be"  # Your Mediastack API key
categories = ["business", "entertainment", "general", "health", "science", "sports", "technology"]
countries = ["us", "in", "gb", "de"]  # USA, India, UK, Germany
ARTICLES_PER_CATEGORY = 150
PAGE_SIZE = 100  # Mediastack max limit per request
BASE_URL = "http://api.mediastack.com/v1/news"
# ----------------------------------------

# Use current script directory
OUTPUT_FOLDER = os.path.dirname(os.path.abspath(__file__))

# ---------------- FETCH NEWS ----------------
for category in categories:
    print(f"Fetching category: {category}...")
    all_articles = []
    offset = 0

    seen_urls = set()  # Track URLs to avoid duplicates
    
    while len(all_articles) < ARTICLES_PER_CATEGORY:
        params = {
            "access_key": API_KEY,
            "categories": category,
            "countries": ",".join(countries),
            "limit": PAGE_SIZE,
            "offset": offset,
            "languages": "en",
            "sort": "published_desc",
        }

        try:
            response = requests.get(BASE_URL, params=params)
            
            if response.status_code != 200:
                print(f"❌ API Error {response.status_code} for {category}")
                break
                
            data = response.json()

            if "data" not in data or not data["data"]:
                print(f"⚠️ No more news for {category} at offset {offset}.")
                break

            # Filter out duplicates
            new_articles = []
            for article in data["data"]:
                if article.get("url") and article["url"] not in seen_urls:
                    seen_urls.add(article["url"])
                    new_articles.append(article)
            
            all_articles.extend(new_articles)
            offset += PAGE_SIZE

            if len(data["data"]) < PAGE_SIZE:
                # No more articles returned
                break

            time.sleep(1)  # prevent hitting API limits
        except Exception as e:
            print(f"❌ Error fetching {category} at offset {offset}: {e}")
            break

    # Trim to desired max articles
    all_articles = all_articles[:ARTICLES_PER_CATEGORY]

    # Transform articles to match your app's expected format
    transformed_articles = []
    for article in all_articles:
        transformed_article = {
            "title": article.get("title", ""),
            "description": article.get("description", ""),
            "url": article.get("url", ""),
            "image": article.get("image", ""),
            "published_at": article.get("published_at", ""),
            "author": article.get("author", "Unknown"),
            "source": article.get("source", "Unknown")
        }
        transformed_articles.append(transformed_article)
    
    # Save JSON file in same directory as script
    filename = os.path.join(OUTPUT_FOLDER, f"{category}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump({
            "status": "ok",
            "totalResults": len(transformed_articles),
            "articles": transformed_articles
        }, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(transformed_articles)} articles to {filename}\n")

print("All category files updated successfully in script directory!")
