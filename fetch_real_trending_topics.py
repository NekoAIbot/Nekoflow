import os
import json
import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Path constants
NICHES_JSON = "niches.json"
BASE_TRENDING_DIR = "trending_topics"

# Number of videos to fetch per channel (you can adjust this)
VIDEOS_PER_CHANNEL = 3

def load_niches():
    """
    Load the niches dictionary from niches.json.
    Expected structure: { niche_name: [ { "channel_name": ..., "channel_id": ... }, ... ], ... }
    """
    if os.path.isfile(NICHES_JSON):
        with open(NICHES_JSON, "r", encoding="utf-8") as f:
            niches = json.load(f)
        return niches
    else:
        print(f"⚠️ {NICHES_JSON} not found. Exiting...")
        exit(1)

def initialize_trending_folders(niches):
    """
    Ensure the base trending_topics folder and subfolders for each niche exist.
    """
    os.makedirs(BASE_TRENDING_DIR, exist_ok=True)
    for niche in niches.keys():
        niche_dir = os.path.join(BASE_TRENDING_DIR, niche)
        os.makedirs(niche_dir, exist_ok=True)

def get_youtube_service():
    """
    Create and return a YouTube API client using the provided API key.
    """
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def fetch_channel_trending_videos(youtube, channel_id):
    """
    Uses the YouTube API 'search.list' endpoint to fetch videos from a given channel.
    Returns a list of topics (video titles) for the channel.
    """
    topics = []
    try:
        # The search list call returns a list of video resources for the channel.
        request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            maxResults=VIDEOS_PER_CHANNEL,
            order="viewCount",
            type="video"
        )
        response = request.execute()
        items = response.get("items", [])
        for item in items:
            # Extract the video title and published time (for uniqueness) from snippet.
            snippet = item.get("snippet", {})
            title = snippet.get("title", "Untitled")
            published_at = snippet.get("publishedAt", "unknown")
            # You can combine these to create a unique topic string; adjust format as needed.
            topic = f"{title} (Published: {published_at})"
            topics.append(topic)
    except HttpError as e:
        error_details = e.error_details if hasattr(e, 'error_details') else str(e)
        print(f"Error fetching videos for channel {channel_id}: {error_details}")
    except Exception as e:
        print(f"Unexpected error fetching videos for channel {channel_id}: {e}")
    return topics

def save_topics_for_niche(niche, channel_topics):
    """
    Saves each trending topic as a separate text file under trending_topics/<niche>/.
    channel_topics: a dictionary { channel_id: [topic1, topic2, ...], ... }
    """
    niche_dir = os.path.join(BASE_TRENDING_DIR, niche)
    for channel_id, topics in channel_topics.items():
        for index, topic in enumerate(topics, start=1):
            # Create a unique filename using the channel id and index
            filename = f"{channel_id}_{index:03d}.txt"
            filepath = os.path.join(niche_dir, filename)
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(topic)
                print(f"✅ Saved topic to {filepath}")
            except Exception as e:
                print(f"Error writing topic for channel {channel_id}: {e}")

def process_niche(niche, channels, youtube):
    """
    For a given niche and its list of channels, fetch trending video topics and save them.
    """
    print(f"\n🔍 Processing niche: {niche}")
    channel_topics = {}  # Dictionary to hold topics per channel

    for channel in channels:
        channel_name = channel.get("channel_name", "Unknown Channel")
        channel_id = channel.get("channel_id")
        if not channel_id:
            print(f"⚠️ Skipping channel {channel_name} (no channel_id provided)")
            continue
        print(f"Fetching videos for '{channel_name}' ({channel_id}) in niche '{niche}'...")
        topics = fetch_channel_trending_videos(youtube, channel_id)
        if topics:
            channel_topics[channel_id] = topics
        else:
            print(f"⚠️ No topics found for channel {channel_name}.")

        # Sleep briefly to avoid hitting rate limits
        time.sleep(1)

    if channel_topics:
        save_topics_for_niche(niche, channel_topics)
    else:
        print(f"⚠️ No trending topics were fetched for niche '{niche}'.")

def main():
    print("🚀 Fetching trending topics for all niches in niches.json...")
    niches_data = load_niches()
    initialize_trending_folders(niches_data)
    youtube = get_youtube_service()

    for niche, channels in niches_data.items():
        process_niche(niche, channels, youtube)

    print("✅ Finished fetching trending topics!")

if __name__ == "__main__":
    main()
