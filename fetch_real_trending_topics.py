#!/usr/bin/env python3
import os
import time
import json
from datetime import datetime, timedelta

import feedparser
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import praw
import tweepy

from dotenv import load_dotenv

# Load environment variables
load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# ---------- CONFIGURATION ----------
BASE_TRENDING_DIR = "trending_topics"
NEWS_THRESHOLD = 10  # total topics required (news + YouTube + Reddit + Twitter)
MAX_RESULTS_PER_SOURCE = 5
PUBLISHED_AFTER = (datetime.utcnow() - timedelta(days=30)).isoformat("T") + "Z"
# -----------------------------------

# --- Candidate niches (a large set of candidate query keywords; you can later update this list automatically) ---
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
    # … extend this list as desired.
]

# --- Helper Functions ---

def initialize_base_folders():
    """Create the base folder for trending topics."""
    os.makedirs(BASE_TRENDING_DIR, exist_ok=True)

def get_youtube_service():
    """Initialize and return the YouTube API service."""
    try:
        service = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        return service
    except Exception as e:
        print(f"⚠️ Error initializing YouTube service: {e}")
        return None

def get_reddit_instance():
    """Return a PRAW Reddit instance."""
    try:
        reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                             client_secret=REDDIT_CLIENT_SECRET,
                             user_agent=REDDIT_USER_AGENT)
        return reddit
    except Exception as e:
        print(f"⚠️ Error initializing Reddit instance: {e}")
        return None

def get_twitter_client():
    """Return a Tweepy client for Twitter API v2."""
    try:
        client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
        return client
    except Exception as e:
        print(f"⚠️ Error initializing Twitter client: {e}")
        return None

def fetch_google_news_topics(niche):
    """Fetch topics from Google News RSS for the given niche."""
    topics = []
    rss_url = f"https://news.google.com/rss/search?q={niche}&hl=en-US&gl=US&ceid=US:en"
    try:
        feed = feedparser.parse(rss_url)
        for entry in feed.entries[:MAX_RESULTS_PER_SOURCE]:
            title = entry.get("title", "").strip()
            published = entry.get("published", "unknown")
            if title:
                topic = f"{title} (Published: {published})"
                topics.append(topic)
    except Exception as e:
        print(f"❌ Error fetching news topics for niche '{niche}': {e}")
    return topics

def fetch_youtube_topics_query(youtube, niche):
    """Fetch topics from YouTube API using a query search."""
    topics = []
    try:
        request = youtube.search().list(
            part="snippet",
            q=niche,
            maxResults=MAX_RESULTS_PER_SOURCE,
            order="viewCount",
            type="video",
            publishedAfter=PUBLISHED_AFTER
        )
        response = request.execute()
        for item in response.get("items", []):
            snippet = item.get("snippet", {})
            title = snippet.get("title", "").strip()
            published_at = snippet.get("publishedAt", "unknown")
            if title:
                topic = f"{title} (Published: {published_at})"
                topics.append(topic)
    except HttpError as e:
        print(f"❌ Error fetching YouTube topics for niche '{niche}': {e}")
    except Exception as e:
        print(f"❌ Unexpected error fetching YouTube topics for niche '{niche}': {e}")
    return topics

def fetch_reddit_topics(reddit, niche):
    """Fetch trending submission titles from a Reddit search for the given niche."""
    topics = []
    try:
        # Searching across Reddit (you may tweak the search parameters)
        query = niche
        for submission in reddit.subreddit("all").search(query, sort="top", limit=MAX_RESULTS_PER_SOURCE):
            title = submission.title.strip()
            if title:
                topic = f"{title} (Reddit)"
                topics.append(topic)
    except Exception as e:
        print(f"❌ Error fetching Reddit topics for niche '{niche}': {e}")
    return topics

def fetch_twitter_topics(client, niche):
    """Fetch recent tweets for the given niche. (Here we will use a simplified search.)"""
    topics = []
    try:
        # Using Twitter recent search endpoint – note that Tweets must be public.
        query = f'"{niche}" -is:retweet lang:en'
        tweets = client.search_recent_tweets(query=query, max_results=MAX_RESULTS_PER_SOURCE)
        if tweets.data:
            for tweet in tweets.data:
                text = tweet.text.strip().split("\n")[0]
                topic = f"{text} (Tweet)"
                topics.append(topic)
    except Exception as e:
        print(f"❌ Error fetching Twitter topics for niche '{niche}': {e}")
    return topics

def score_niche(niche, youtube, reddit, twitter):
    """Return a score for the given niche based on the number of topics from each source."""
    news_topics = fetch_google_news_topics(niche)
    yt_topics = fetch_youtube_topics_query(youtube, niche) if youtube else []
    reddit_topics = fetch_reddit_topics(reddit, niche) if reddit else []
    twitter_topics = fetch_twitter_topics(twitter, niche) if twitter else []
    total = len(news_topics) + len(yt_topics) + len(reddit_topics) + len(twitter_topics)
    return total, news_topics, yt_topics, reddit_topics, twitter_topics

def filter_trending_niches(candidate_niches, youtube, reddit, twitter):
    """Return a dict of niches that score above the threshold."""
    trending = {}
    print("🔎 Evaluating candidate niches based on available trending topics...")
    for niche in candidate_niches:
        total, news_topics, yt_topics, reddit_topics, twitter_topics = score_niche(niche, youtube, reddit, twitter)
        print(f"  - '{niche}' scored {total} (News: {len(news_topics)}, YouTube: {len(yt_topics)}, Reddit: {len(reddit_topics)}, Twitter: {len(twitter_topics)})")
        if total >= NEWS_THRESHOLD:
            trending[niche] = {
                "news": news_topics,
                "youtube": yt_topics,
                "reddit": reddit_topics,
                "twitter": twitter_topics
            }
    return trending

def save_topics(niche, topics):
    """Save topics as individual text files in trending_topics/<niche>."""
    niche_dir = os.path.join(BASE_TRENDING_DIR, niche)
    os.makedirs(niche_dir, exist_ok=True)
    unique_topics = list({t for t in topics if t})
    unique_topics.sort()
    for idx, topic in enumerate(unique_topics, start=1):
        filename = f"{niche.replace(' ', '_')}_{idx:03d}.txt"
        filepath = os.path.join(niche_dir, filename)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(topic)
            print(f"✅ Saved topic: {filepath}")
        except Exception as e:
            print(f"❌ Error saving topic {filepath}: {e}")

def process_trending_niches(trending_niches):
    """For each trending niche, combine topics from all sources and save them."""
    for niche, sources in trending_niches.items():
        print(f"\n🔍 Processing trending niche: {niche}")
        combined = sources.get("news", []) + sources.get("youtube", []) \
                   + sources.get("reddit", []) + sources.get("twitter", [])
        if combined:
            save_topics(niche, combined)
        else:
            print(f"⚠️ No topics to save for '{niche}'.")

def main():
    print("🚀 Fetching trending topics for candidate niches...\n")
    initialize_base_folders()
    youtube = get_youtube_service()
    reddit = get_reddit_instance()
    twitter = get_twitter_client()
    trending_niches = filter_trending_niches(candidate_niches, youtube, reddit, twitter)

    if trending_niches:
        print("\n✅ Trending niches identified:")
        for niche in trending_niches:
            count = (len(trending_niches[niche]["news"]) +
                     len(trending_niches[niche]["youtube"]) +
                     len(trending_niches[niche]["reddit"]) +
                     len(trending_niches[niche]["twitter"]))
            print(f"   • {niche} ({count} topics)")
    else:
        print("⚠️ No trending niches were found based on current criteria.")

    process_trending_niches(trending_niches)
    print("\n✅ Finished fetching and saving trending topics for all trending niches!")

if __name__ == "__main__":
    main()
