import os
import json
import requests
import feedparser
import hashlib

HEADERS = {'User-Agent': 'Mozilla/5.0'}
GOOGLE_NEWS_TEMPLATE = "https://news.google.com/rss/search?q={}&hl=en-US&gl=US&ceid=US:en"

def load_niches(json_path="niches.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def safe_filename(text):
    """Create a safe hashed filename for each topic."""
    return hashlib.md5(text.encode()).hexdigest()[:12] + ".txt"

def fetch_google_news(keyword):
    url = GOOGLE_NEWS_TEMPLATE.format(keyword.replace(" ", "+"))
    feed = feedparser.parse(url)
    titles = []
    for entry in feed.entries:
        title = entry.title.strip()
        if len(title) > 15:
            titles.append(title)
    return titles

def save_titles(niche, titles):
    folder = os.path.join("trending_topics", niche)
    os.makedirs(folder, exist_ok=True)

    for title in titles:
        filename = safe_filename(title)
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(title)

def main():
    print("🚀 Fetching trending topics for all niches in niches.json...")
    niches = load_niches()

    for niche in niches:
        print(f"🔍 Fetching for niche: {niche}")
        titles = fetch_google_news(niche)
        if not titles:
            print(f"⚠️ No results found for: {niche}")
            continue
        save_titles(niche, titles[:10])  # Save top 10 per niche

    print("\n✅ Finished fetching real trending topics!")

if __name__ == "__main__":
    main()
