import os
import json
import datetime
import requests
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

# YouTube API key from .env
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

# Path to niche definitions file
NICHE_FILE = "niches.json"
BACKTEST_DIR = "backtest_data"
os.makedirs(BACKTEST_DIR, exist_ok=True)

# Text-generation-webui endpoint (update if necessary)
TGW_API_URL = os.getenv("TGW_API_URL", "http://localhost:7860/api/v1/completions")  # example endpoint

def load_niches():
    """Loads niche definitions from niches.json."""
    if os.path.exists(NICHE_FILE):
        with open(NICHE_FILE, "r", encoding="utf-8") as f:
            niches = json.load(f)
        return niches
    else:
        print(f"Error: {NICHE_FILE} not found.")
        return {}

def fetch_channel_videos(channel_id, max_results=5):
    """
    Fetches the top 'max_results' recent videos from a channel.
    """
    try:
        request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            order="viewCount",   # ordering by view count; adjust as needed
            maxResults=max_results,
            type="video"
        )
        response = request.execute()
        videos = response.get("items", [])
        return videos
    except Exception as e:
        print(f"Error fetching videos for channel {channel_id}: {e}")
        return []

def fetch_video_transcript(video_id):
    """Attempts to fetch transcript for a given video ID."""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([t["text"] for t in transcript_list])
        return transcript_text
    except (TranscriptsDisabled, NoTranscriptFound):
        return ""
    except Exception as e:
        print(f"Error fetching transcript for video {video_id}: {e}")
        return ""

def harvest_data():
    """
    Harvests backtest data for all niches and channels.
    Saves collected data in a JSON file for later analysis.
    """
    niches = load_niches()
    all_data = {}
    for niche, channels in niches.items():
        all_data[niche] = []
        for channel in channels:
            channel_name = channel.get("channel_name", "Unknown Channel")
            channel_id = channel.get("channel_id", "")
            print(f"Fetching videos for '{channel_name}' ({channel_id}) in niche '{niche}'...")
            videos = fetch_channel_videos(channel_id)
            for video in videos:
                video_id = video["id"]["videoId"]
                snippet = video["snippet"]
                video_data = {
                    "video_id": video_id,
                    "title": snippet.get("title", ""),
                    "description": snippet.get("description", ""),
                    "published_at": snippet.get("publishedAt", ""),
                    "channel_name": channel_name,
                    "transcript": fetch_video_transcript(video_id)
                }
                all_data[niche].append(video_data)
    
    output_file = os.path.join(BACKTEST_DIR, "backtest_data.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4)
    print(f"Backtest data saved to {output_file}")

def generate_refined_script_with_tgw(prompt_text):
    """
    Uses the text-generation-webui API to generate a refined script.
    """
    payload = {
        "prompt": prompt_text,
        "max_length": 400,
        "temperature": 0.9,
        "top_p": 0.95,
        "do_sample": True,
        "num_return_sequences": 1,
        "stop": ["\n\n"]
    }
    try:
        response = requests.post(TGW_API_URL, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            # Adjust extraction based on API response structure
            return result["choices"][0]["text"].strip()
        else:
            print(f"Error: TGW API responded with status {response.status_code}")
            return ""
    except Exception as e:
        print(f"Error calling TGW API: {e}")
        return ""

if __name__ == "__main__":
    harvest_data()

    # Example: Generate a refined script for backtest analysis using TGW
    sample_prompt = ("Write a compelling, human-like YouTube video script in the Finance niche "
                     "about the trends in the US economy before Trump's tariff chaos. "
                     "Make sure it starts with an engaging hook and ends with a clear call to action.")
    refined_script = generate_refined_script_with_tgw(sample_prompt)
    print("\nGenerated Script Example:\n")
    print(refined_script)
