#!/usr/bin/env python3
import os
import re
import json
import time
import random
from datetime import datetime, timedelta, timezone
from urllib.parse import quote_plus

import feedparser
import snscrape.modules.twitter as sntwitter
import praw
import pandas as pd
from pytrends.request import TrendReq
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

# ---------- CONFIGURATION ----------
BASE_TRENDING_DIR = "trending_topics"
NEWS_THRESHOLD = 10
MAX_RESULTS_PER_SOURCE = 5
PUBLISHED_AFTER = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat().replace("+00:00", "Z")
# -----------------------------------

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
    os.makedirs(BASE_TRENDING_DIR, exist_ok=True)
    os.makedirs("backtest_data", exist_ok=True)

def sanitize_query(query):
    return re.sub(r'\s+', '+', query)

def get_youtube_service():
    try:
        return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    except Exception as e:
        print(f"⚠️ YouTube service error: {e}")
        return None

def get_reddit_instance():
    try:
        return praw.Reddit(client_id=REDDIT_CLIENT_ID,
                           client_secret=REDDIT_CLIENT_SECRET,
                           user_agent=REDDIT_USER_AGENT)
    except Exception as e:
        print(f"⚠️ Reddit service error: {e}")
        return None

def fetch_google_news_topics(niche):
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
            title = item.get("snippet", {}).get("title", "").strip()
            published = item.get("snippet", {}).get("publishedAt", "unknown")
            if title:
                topics.append(f"{title} (Published: {published})")
    except Exception as e:
        print(f"❌ YouTube error for '{niche}': {e}")
    return topics

def fetch_reddit_topics(reddit, niche):
    topics = []
    try:
        for submission in reddit.subreddit("all").search(niche, sort="top", limit=MAX_RESULTS_PER_SOURCE):
            topics.append(f"{submission.title.strip()} (Reddit)")
    except Exception as e:
        print(f"❌ Reddit error for '{niche}': {e}")
    return topics

def fetch_twitter_topics(niche):
    topics = []
    try:
        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(f'"{niche}" lang:en').get_items()):
            if i >= MAX_RESULTS_PER_SOURCE:
                break
            topics.append(f"{tweet.content.strip().splitlines()[0]} (Tweet)")
    except Exception as e:
        print(f"❌ Twitter scrape error for '{niche}': {e}")
    return topics

def fetch_google_trends_topics(niche):
    topics = []
    delay = 5
    for attempt in range(3):
        try:
            pytrend = TrendReq(hl='en-US', tz=360)
            pytrend.build_payload([niche], cat=0, timeframe='now 7-d', geo='', gprop='')
            trends = pytrend.interest_over_time()
            if not trends.empty:
                trends_list = trends[niche].to_list()
                if max(trends_list) > 50:
                    topics.append(f"{niche} trending on Google Trends")
            break  # success, exit loop
        except Exception as e:
            print(f"🔁 Google Trends error for '{niche}', retrying in {delay}s... ({e})")
            time.sleep(delay)
            delay *= 2
    return topics

def fetch_trending_topics_for_niche(niche, youtube, reddit, twitter):
    topics = set()
    try: topics.update(fetch_google_news_topics(niche))
    except: pass
    try: topics.update(fetch_youtube_topics(youtube, niche)) if youtube else None
    except: pass
    try: topics.update(fetch_reddit_topics(reddit, niche)) if reddit else None
    except: pass
    try: topics.update(fetch_twitter_topics(niche))
    except: pass
    try: topics.update(fetch_google_trends_topics(niche))
    except: pass
    return list(topics)

def save_topics(niche, topics):
    directory = os.path.join(BASE_TRENDING_DIR, niche)
    os.makedirs(directory, exist_ok=True)
    for idx, topic in enumerate(sorted(set(topics)), 1):
        filename = os.path.join(directory, f"{niche.replace(' ', '_')}_{idx:03d}.txt")
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(topic)
            print(f"✅ Saved topic: {filename}")
        except Exception as e:
            print(f"❌ Error saving {filename}: {e}")

def process_niches(niches, youtube, reddit, twitter):
    all_trending = {}
    print("🔎 Evaluating candidate niches based on available trending topics...\n")
    for niche in niches:
        print(f"\n🔍 Processing niche: {niche}")
        topics = fetch_trending_topics_for_niche(niche, youtube, reddit, twitter)
        score = len(topics)
        print(f"  - '{niche}' scored {score} topics")
        if score >= NEWS_THRESHOLD:
            save_topics(niche, topics)
            all_trending[niche] = topics
        else:
            print(f"⚠️ Not enough topics for '{niche}' ({score} found)")
    with open("backtest_data/trending_data.json", "w", encoding="utf-8") as f:
        json.dump(all_trending, f, indent=2)
    return all_trending

def main():
    print("🚀 Fetching trending topics for candidate niches...\n")
    initialize_base_folders()
    youtube = get_youtube_service()
    reddit = get_reddit_instance()
    twitter = None  # no API needed with snscrape
    trending = process_niches(candidate_niches, youtube, reddit, twitter)
    if trending:
        print("\n✅ Trending niches and topics have been saved successfully!")
    else:
        print("\n⚠️ No trending niches met the threshold.")

if __name__ == "__main__":
    main()
