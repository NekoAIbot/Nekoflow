import os
import feedparser
import requests
from dotenv import load_dotenv

# Load API keys
load_dotenv()
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")

def fetch_newsdata_titles():
    try:
        url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_API_KEY}&country=us&language=en&category=top"
        response = requests.get(url)
        data = response.json()
        articles = data.get("results", [])
        titles = [article["title"] for article in articles if "title" in article]
        return titles
    except Exception as e:
        print(f"❌ NewsData fetch error: {e}")
        return []

def fetch_reddit_titles():
    try:
        url = "https://www.reddit.com/r/news/top/.json?t=day&limit=15"
        headers = {"User-agent": "NekoFlowBot 1.0"}
        response = requests.get(url, headers=headers)
        posts = response.json()["data"]["children"]
        titles = [post["data"]["title"] for post in posts]
        return titles
    except Exception as e:
        print(f"❌ Reddit fetch error: {e}")
        return []

def fetch_google_rss_titles():
    try:
        url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(url)
        titles = [entry.title for entry in feed.entries]
        return titles
    except Exception as e:
        print(f"❌ Google RSS fetch error: {e}")
        return []

def combine_sources():
    print("📡 Gathering trending topics...\n")
    
    titles_newsdata = fetch_newsdata_titles()
    titles_reddit = fetch_reddit_titles()
    titles_google = fetch_google_rss_titles()

    combined = titles_newsdata + titles_reddit + titles_google
    seen = set()
    unique_titles = []

    for title in combined:
        cleaned = title.strip()
        if cleaned.lower() not in seen:
            unique_titles.append(cleaned)
            seen.add(cleaned.lower())

    return unique_titles[:15]  # Limit to top 15

# ✅ No auto-execution here. Only import this module.
