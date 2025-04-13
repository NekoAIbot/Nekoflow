import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

def search_pexels_video(query, per_page=5):
    url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": per_page}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def download_video(video_url, output_path):
    response = requests.get(video_url, stream=True)
    response.raise_for_status()
    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"✅ Video downloaded and saved as: {output_path}")

def main():
    # Define the search query for a tech background looping video
    query = "tech background loop"
    try:
        results = search_pexels_video(query)
        videos = results.get("videos", [])
        if not videos:
            print("❌ No videos found for the query.")
            return

        # For this example, we want the best quality video that matches the script's theme.
        # We'll iterate through the videos and their video_files and choose the one with the highest resolution.
        best_video_url = None
        best_resolution = 0

        for video in videos:
            video_files = video.get("video_files", [])
            # Sort by width (largest first)
            sorted_files = sorted(video_files, key=lambda vf: vf.get("width", 0), reverse=True)
            if sorted_files:
                candidate = sorted_files[0]  # the best quality in this video result
                width = candidate.get("width", 0)
                if width > best_resolution:
                    best_resolution = width
                    best_video_url = candidate.get("link")

        if not best_video_url:
            print("❌ No suitable video file found in the results.")
            return

        # Ensure assets folder exists
        assets_dir = "assets"
        os.makedirs(assets_dir, exist_ok=True)
        output_path = os.path.join(assets_dir, "bg_tech_loop.mp4")
        download_video(best_video_url, output_path)
    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    main()
