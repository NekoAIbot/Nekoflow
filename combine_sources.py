import os
import json
import requests
import feedparser
import praw
from dotenv import load_dotenv

import json

USED_TITLES_FILE = "used_titles.json"

def load_used_titles():
    if os.path.exists(USED_TITLES_FILE):
        with open(USED_TITLES_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_used_titles(titles):
    with open(USED_TITLES_FILE, "w", encoding="utf-8") as f:
        json.dump(list(titles), f, ensure_ascii=False, indent=2)

# Load environment variables
load_dotenv()
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")

# ========== Data Fetchers ==========

def fetch_newsdata_titles():
    try:
        url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_API_KEY}&country=us&language=en&category=top"
        response = requests.get(url)
        data = response.json()
        articles = data.get("results", [])
        titles = [article["title"] for article in articles if "title" in article]
        print("NewsData titles:", titles)
        return titles
    except Exception as e:
        print(f"❌ NewsData fetch error: {e}")
        return []

def fetch_reddit_titles():
    print("🔍 Fetching Reddit trending titles with PRAW...")
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent="NekoFlowBot/0.1 by yourusername"
    )
    try:
        hot_posts = reddit.subreddit("popular").hot(limit=15)
        titles = [post.title for post in hot_posts]
        print(f"✅ Reddit titles: {titles[:5]}...")
        return titles
    except Exception as e:
        print(f"❌ Reddit fetch error: {e}")
        return []

def fetch_google_rss_titles():
    try:
        url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(url)
        titles = [entry.title for entry in feed.entries]
        print("Google RSS titles:", titles)
        return titles
    except Exception as e:
        print(f"❌ Google RSS fetch error: {e}")
        return []

def fetch_hackernews_titles(limit=15):
    print("🔐 Fetching Hacker News top stories...")
    try:
        url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        top_ids = requests.get(url).json()[:100]

        # Cybersecurity keywords
        keywords = set(k.lower() for k in ["cyber", "hacking", "breach", "exploit", "vulnerability", "cve", "security", "ransomware", "malware", "encryption", "phishing", "tor", "pentest", "infosec", "cyber attack", "zero-day", "ctf", "ddos", "reverse engineering", "firewall", "siem", "defcon", "blackhat", "cyberwarfare", "botnet", "spyware", "tls", "kerberos", "ssh", "sql injection", "mitre", "patch", "token", "sandbox", "zero trust", "firmware", "man-in-the-middle", "session hijack", "payload", "auth", "prompt injection", "data poisoning", "tracking", "facial recognition", "anonymity", "dark web", "privacy", "surveillance"])
        
        titles = []
        for story_id in top_ids:
            story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            story = requests.get(story_url).json()
            if story and "title" in story:
                title = story["title"]
                if any(k in title.lower() for k in keywords):
                    titles.append(title)
            if len(titles) >= limit:
                break
        print(f"✅ Hacker News titles: {len(titles)}")
        return titles
    except Exception as e:
        print(f"❌ Hacker News fetch error: {e}")
        return []

# ========== Tagging Logic ==========

def categorize_title(title: str) -> list[str]:
    title = title.lower()
    tags = []
    if any(k in title for k in ["hack", "cyber", "malware", "phishing", "breach", "exploit", "cve", "security"]):
        tags.append("Cybersecurity")
    if any(k in title for k in ["trump", "biden", "congress", "election", "senate", "parliament", "government"]):
        tags.append("Politics")
    if any(k in title for k in ["nasa", "space", "neutrino", "physics", "experiment", "galaxy", "brain", "science"]):
        tags.append("Science")
    if any(k in title for k in ["ai", "gpt", "openai", "machine learning", "chatgpt", "deep learning"]):
        tags.append("AI")
    if any(k in title for k in ["stock", "economy", "inflation", "tariff", "market", "recession", "interest rate"]):
        tags.append("Finance")
    if any(k in title for k in ["vaccine", "covid", "measles", "tumor", "health", "als", "clinic", "hospital"]):
        tags.append("Health")
    if any(k in title for k in ["actor", "movie", "film", "show", "euphoria", "grey’s anatomy", "netflix"]):
        tags.append("Entertainment")
    if any(k in title for k in ["football", "nba", "nfl", "match", "game", "sports", "draft", "ufc", "mclaren"]):
        tags.append("Sports")
    return tags or ["Uncategorized"]

# ========== Main Combine Logic ==========

def combine_sources():
    print("📡 Gathering trending topics...\n")
    
    all_titles = []

    newsdata_titles = fetch_newsdata_titles()
    all_titles.extend(newsdata_titles)

    reddit_titles = fetch_reddit_titles()
    all_titles.extend(reddit_titles)

    rss_titles = fetch_google_rss_titles()
    all_titles.extend(rss_titles)

    hn_titles = fetch_hackernews_titles()
    all_titles.extend(hn_titles)

    # ✅ Load used titles and filter them
    used_titles = load_used_titles()
    new_titles = [t for t in all_titles if t not in used_titles]

    # ✅ Update used titles set
    updated_used = used_titles.union(new_titles)
    save_used_titles(updated_used)

    # ✅ Deduplicate new only
    unique_titles = list(dict.fromkeys(new_titles))

    print(f"\nTotal unique new titles: {len(unique_titles)}")
    if unique_titles:
        print("\n📰 Sample Trending Titles:")
        for idx, title in enumerate(unique_titles[:15], 1):
            print(f"{idx}. {title}")
    else:
        print("⚠️ No new topics found. Try again later or clear cache.")

    # Optionally: Save to trending_topics.json
    if unique_titles:
        with open("trending_topics.json", "w", encoding="utf-8") as f:
            json.dump(unique_titles, f, ensure_ascii=False, indent=2)
        print("\n📦 Trending topics saved to trending_topics.json")

    return unique_titles

# ========== Run if main ==========

if __name__ == "__main__":
    topics = combine_sources()
    if not topics:
        print("⚠️ No trending titles found.")
