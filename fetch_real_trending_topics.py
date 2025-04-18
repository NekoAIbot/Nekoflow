#!/usr/bin/env python3
import os
import re
import json
import time
import random
from datetime import datetime, timedelta, timezone
from urllib.parse import quote_plus

import feedparser
import praw
import pandas as pd
from pytrends.request import TrendReq
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# -----------------------------------------
# Try to import snscrape; if it fails, disable Twitter scraping
# -----------------------------------------
try:
    import snscrape.modules.twitter as sntwitter
    SNTWITTER_AVAILABLE = True
except Exception as e:
    print(f"⚠️ snscrape import failed ({e}); Twitter topics will be skipped.")
    SNTWITTER_AVAILABLE = False

# Load environment variables
load_dotenv()
YOUTUBE_API_KEY       = os.getenv("YOUTUBE_API_KEY")
REDDIT_CLIENT_ID      = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET  = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT     = os.getenv("REDDIT_USER_AGENT")

# ---------- CONFIGURATION ----------
BASE_TRENDING_DIR      = "trending_topics"
NEWS_THRESHOLD        = 10
MAX_RESULTS_PER_SOURCE = 5
# Use a timezone‑aware datetime string for publishedAfter
PUBLISHED_AFTER       = (datetime.now(timezone.utc) - timedelta(days=30))\
                            .isoformat().replace("+00:00", "Z")
# -----------------------------------

# List of candidate niches (you can extend this later or generate dynamically)
candidate_niches = [
    "call of duty", "cod mobile", "cod warzone", "apex legends", "fortnite", "pubg mobile",
    "league of legends", "dota2", "overwatch", "valorant", "esports", "gaming", "indie games",
    "retro gaming", "mobile gaming", "pc gaming", "console gaming", "streaming", "reaction",
    "prank", "challenge", "short film", "book review", "literature", "instrumental", "cover music",
    "original music", "movie review", "tv review", "tutorial", "programming", "coding",
    "language learning", "sustainable", "eco friendly", "tech reviews", "gadgets", "lifestyle vlog",
    "daily vlog", "travel vlog", "science experiments", "space", "engineering", "robotics",
    "podcasting", "fashion design", "travel tips", "fitness challenges", "art", "crafts",
    "self improvement", "mindset", "reality tv", "celeb news", "news analysis", "sports",
    "interviews", "tech tutorials", "vfx", "animation tutorials", "3d design", "photography",
    "filmmaking", "investigative journalism", "documentary filmmaking", "comedy sketches",
    "standup comedy", "rants", "motivational speeches", "music instruments", "vlogging tutorials",
    "entrepreneurship tips", "digital marketing", "social media tips", "social innovation",
    "home decor", "gardening tips", "cooking recipes", "baking tutorials", "wine reviews",
    "beer reviews", "celebrity", "makeup", "hairstyling", "skincare", "yoga", "meditation",
    "mindfulness", "basketball", "football", "soccer", "baseball", "hockey", "cricket",
    "rugby", "boxing", "mma", "business"
]

def initialize_base_folders():
    """Create the base folder for trending topics."""
    os.makedirs(BASE_TRENDING_DIR, exist_ok=True)

def sanitize_query(query):
    """Sanitize query strings by replacing whitespace with '+'."""
    return re.sub(r'\s+', '+', query)

def get_youtube_service():
    """Initialize and return the YouTube API service."""
    try:
        return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    except Exception as e:
        print(f"⚠️ YouTube service error: {e}")
        return None

def get_reddit_instance():
    """Return a PRAW Reddit instance."""
    try:
        return praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )
    except Exception as e:
        print(f"⚠️ Reddit service error: {e}")
        return None

def fetch_google_news_topics(niche):
    """Fetch topics from Google News RSS for the given niche."""
    topics = []
    try:
        rss_url = f"https://news.google.com/rss/search?q={quote_plus(niche)}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        for entry in feed.entries[:MAX_RESULTS_PER_SOURCE]:
            title = entry.get("title", "").strip()
            published = entry.get("published", "unknown")
            if title:
                topics.append(f"{title} (Published: {published})")
    except Exception as e:
        print(f"❌ News error for '{niche}': {e}")
    return topics

def fetch_youtube_topics(youtube, niche):
    """Fetch topics from YouTube API using a query search."""
    topics = []
    try:
        request = youtube.search().list(
            part="snippet",
            q=sanitize_query(niche),
            maxResults=MAX_RESULTS_PER_SOURCE,
            order="viewCount",
            type="video",
            publishedAfter=PUBLISHED_AFTER
        )
        response = request.execute()
        for item in response.get("items", []):
            snip = item.get("snippet", {})
            title = snip.get("title", "").strip()
            pub_at = snip.get("publishedAt", "unknown")
            if title:
                topics.append(f"{title} (Published: {pub_at})")
    except HttpError as e:
        print(f"❌ YouTube error for '{niche}': {e}")
    except Exception as e:
        print(f"❌ Unexpected YouTube error for '{niche}': {e}")
    return topics

def fetch_reddit_topics(reddit, niche):
    """Fetch top Reddit submission titles for the given niche."""
    topics = []
    try:
        for submission in reddit.subreddit("all").search(niche, sort="top", limit=MAX_RESULTS_PER_SOURCE):
            title = submission.title.strip()
            if title:
                topics.append(f"{title} (Reddit)")
    except Exception as e:
        print(f"❌ Reddit error for '{niche}': {e}")
    return topics

def fetch_twitter_topics(niche):
    """Fetch recent tweets using snscrape (if available)."""
    if not SNTWITTER_AVAILABLE:
        return []
    topics = []
    query = f'"{niche}" lang:en'
    try:
        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
            if i >= MAX_RESULTS_PER_SOURCE:
                break
            text = tweet.content.strip().splitlines()[0]
            topics.append(f"{text} (Tweet)")
    except Exception as e:
        print(f"❌ Twitter scrape error for '{niche}': {e}")
    return topics

def fetch_google_trends_topics(niche):
    """Fetch Google Trends interest over time and flag if trending."""
    topics = []
    try:
        pytrend = TrendReq(hl='en-US', tz=360)
        pytrend.build_payload([niche], timeframe='now 7-d', geo='', gprop='')
        df = pytrend.interest_over_time()
        if not df.empty and df[niche].max() > 50:
            topics.append(f"{niche} trending on Google Trends")
        # brief random sleep to avoid rate‑limit bursts
        time.sleep(random.uniform(1, 3))
    except Exception as e:
        print(f"❌ Google Trends error for '{niche}': {e}")
    return topics

def fetch_trending_topics_for_niche(niche, youtube, reddit):
    """Combine all sources for the given niche."""
    topics = set()

    # 1) News
    topics.update(fetch_google_news_topics(niche))

    # 2) YouTube
    if youtube:
        topics.update(fetch_youtube_topics(youtube, niche))

    # 3) Reddit
    if reddit:
        topics.update(fetch_reddit_topics(reddit, niche))

    # 4) Twitter (snscrape)
    topics.update(fetch_twitter_topics(niche))

    # 5) Google Trends
    topics.update(fetch_google_trends_topics(niche))

    return list(topics)

def save_topics(niche, topics):
    """Save each topic into its own .txt under trending_topics/<niche>/."""
    niche_dir = os.path.join(BASE_TRENDING_DIR, niche.replace(" ", "_"))
    os.makedirs(niche_dir, exist_ok=True)
    unique_sorted = sorted(set(topics))
    for idx, topic in enumerate(unique_sorted, start=1):
        fn = f"{niche.replace(' ', '_')}_{idx:03d}.txt"
        path = os.path.join(niche_dir, fn)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(topic)
            print(f"✅ Saved topic: {path}")
        except Exception as e:
            print(f"❌ Error saving {path}: {e}")

def process_niches(niches):
    youtube = get_youtube_service()
    reddit  = get_reddit_instance()
    all_trending = {}

    print("🔎 Evaluating candidate niches based on available trending topics...\n")
    for niche in niches:
        print(f"🔍 Processing niche: {niche}")
        topics = fetch_trending_topics_for_niche(niche, youtube, reddit)
        score  = len(topics)
        print(f"  - '{niche}' scored {score} topics")
        if score >= NEWS_THRESHOLD:
            save_topics(niche, topics)
            all_trending[niche] = topics
        else:
            print(f"⚠️ Not enough topics for '{niche}' (found {score}); skipping.\n")

    # Save raw backtest data
    os.makedirs("backtest_data", exist_ok=True)
    with open("backtest_data/trending_data.json", "w", encoding="utf-8") as f:
        json.dump(all_trending, f, indent=2)

    return all_trending

def main():
    print("🚀 Fetching trending topics for candidate niches...\n")
    initialize_base_folders()
    trending = process_niches(candidate_niches)

    if trending:
        print("\n✅ Trending niches and topics saved successfully!")
    else:
        print("\n⚠️ No niches met the threshold.")

if __name__ == "__main__":
    main()
