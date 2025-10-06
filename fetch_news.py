import requests
import json
import os
import time
from git import Repo, GitCommandError

# ---------------- CONFIG ----------------
API_KEY = "731d73ab4dded5018c85153269160869"  # Your Mediastack API key
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
            data = response.json()

            if "data" not in data or not data["data"]:
                print(f"⚠️ No more news for {category} at offset {offset}.")
                break

            all_articles.extend(data["data"])
            offset += PAGE_SIZE

            if len(data["data"]) < PAGE_SIZE:
                break

            time.sleep(1)  # prevent hitting API limits
        except Exception as e:
            print(f"❌ Error fetching {category} at offset {offset}: {e}")
            break

    # Trim to desired max articles
    all_articles = all_articles[:ARTICLES_PER_CATEGORY]

    # Save JSON file
    filename = os.path.join(OUTPUT_FOLDER, f"{category}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump({
            "status": "ok",
            "totalResults": len(all_articles),
            "articles": all_articles
        }, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved {len(all_articles)} articles to {filename}\n")

# ---------------- PUSH TO GITHUB ----------------
try:
    repo = Repo(OUTPUT_FOLDER)  # Make sure this is the path to your local repo
    repo.git.add(update=True)    # Stage all changed files
    repo.index.commit("Update news JSON files")  # Commit
    origin = repo.remote(name='origin')
    origin.push()  # Push to GitHub
    print("🎉 All changes pushed to GitHub successfully!")
except GitCommandError as e:
    print(f"❌ Git operation failed: {e}")
except Exception as e:
    print(f"❌ Unexpected error during Git push: {e}")
