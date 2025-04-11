import requests
import os
from dotenv import load_dotenv

# Load API keys from .env
load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

def get_youtube_trending(region_code="US", max_results=10):
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": region_code,
        "maxResults": max_results,
        "key": API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"Error {response.status_code}: {response.json()}")
        return []

    trending_videos = response.json().get("items", [])
    results = []

    for video in trending_videos:
        snippet = video["snippet"]
        stats = video.get("statistics", {})
        results.append({
            "title": snippet["title"],
            "channel": snippet["channelTitle"],
            "category": snippet.get("categoryId", "N/A"),
            "views": stats.get("viewCount", "N/A"),
            "description": snippet.get("description", ""),
            "video_url": f"https://www.youtube.com/watch?v={video['id']}"
        })

    return results

# Example usage
if __name__ == "__main__":
    regions = ["US", "NG", "IN", "GB", "JP", "BR", "FR", "DE", "ZA", "KE"]  # You can add more country codes here
    all_trending = {}

    print("\n🔥 Multi-Region YouTube Trends:\n")

    for region in regions:
        print(f"🌍 Region: {region}")
        trending = get_youtube_trending(region_code=region, max_results=10)
        all_trending[region] = trending

        for i, video in enumerate(trending, 1):
            print(f"{i}. {video['title']} ({video['views']} views)")
            print(f"   By: {video['channel']}")
            print(f"   Link: {video['video_url']}\n")

    # You can now use all_trending as input for script generation, filtering, etc.

