# video_maker.py
import os
import asyncio
import subprocess
from pathlib import Path
from voice_engine import generate_voice
from script_optimizer import smart_optimize_response
import requests

def ensure_asset(asset_path, download_url):
    """
    Check if the asset exists. If not, try to download it.
    If download fails, generate a fallback image using Pillow.
    """
    if not os.path.exists(asset_path):
        print(f"Asset '{asset_path}' not found, attempting to download from {download_url} ...")
        try:
            response = requests.get(download_url, timeout=10)
            response.raise_for_status()  # Raise an error for bad status codes
            with open(asset_path, "wb") as f:
                f.write(response.content)
            print(f"Downloaded asset to: {asset_path}")
        except Exception as e:
            print(f"Failed to download asset: {e}. Generating fallback image instead.")
            try:
                from PIL import Image, ImageDraw, ImageFont
                img = Image.new("RGB", (1280, 720), color=(0, 0, 0))
                draw = ImageDraw.Draw(img)
                # Try to use a truetype font, fall back to default if unavailable.
                try:
                    font = ImageFont.truetype("arial.ttf", 40)
                except Exception:
                    font = ImageFont.load_default()
                text = "Background"
                text_width, text_height = draw.textsize(text, font=font)
                x = (1280 - text_width) // 2
                y = (720 - text_height) // 2
                draw.text((x, y), text, fill=(255, 255, 255), font=font)
                img.save(asset_path)
                print(f"Generated fallback image to: {asset_path}")
            except Exception as gen_e:
                print(f"Failed to generate fallback image: {gen_e}")
                raise

def get_background_video(niche):
    # For Tech niche, we expect a looping stock video.
    if niche.lower() == "tech":
        video_path = "assets/bg_tech_loop.mp4"
        if not os.path.exists(video_path):
            print("Tech stock video not found. Please download one or enable auto-downloading for video assets.")
        return video_path
    # Otherwise, return None (we will fall back to a static image)
    return None

def create_video(audio_path, bg_video, output_path):
    if bg_video and os.path.exists(bg_video):
        # Use ffmpeg to loop the background video indefinitely until the audio ends.
        cmd = [
            "ffmpeg",
            "-y",
            "-stream_loop", "-1",  # Loop the video indefinitely
            "-i", bg_video,
            "-i", audio_path,
            "-shortest",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-vf", "scale=1280:720",
            output_path
        ]
    else:
        # Use a fallback static image as background.
        static_image = "assets/static_bg.png"
        # Ensure the static image exists (try to download or generate one automatically)
        fallback_url = "https://dummyimage.com/1280x720/000/fff.png&text=Background"
        ensure_asset(static_image, fallback_url)
        cmd = [
            "ffmpeg",
            "-y",
            "-loop", "1",
            "-i", static_image,
            "-i", audio_path,
            "-shortest",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-vf", "scale=1280:720",
            output_path
        ]
    subprocess.run(cmd, check=True)

def generate_video_from_script(script_path, niche):
    audio_file = "temp_audio.mp3"
    with open(script_path, "r", encoding="utf-8") as f:
        script_text = f.read()
    
    # Optimize the script so it sounds more natural
    optimized_script = smart_optimize_response(script_text)
    print(f"🎙️ Generating voiceover for script: {script_path}")
    asyncio.run(generate_voice(optimized_script, filename=audio_file, niche=niche))
    
    # Select background video if available.
    bg_video = get_background_video(niche)
    
    # Output video will be saved in generated_videos/{niche}
    base_filename = Path(script_path).stem
    output_folder = Path("generated_videos") / niche.lower()
    output_folder.mkdir(parents=True, exist_ok=True)
    output_video_path = output_folder / f"{base_filename}.mp4"
    
    print(f"🎞️ Creating video: {output_video_path}")
    create_video(audio_file, bg_video, str(output_video_path))
    print(f"✅ Saved video to: {output_video_path}")

def run_all_videos():
    base_dir = Path("generated_scripts")
    if not base_dir.exists():
        print("No generated scripts found.")
        return
    
    # Process all niche folders under generated_scripts
    for niche_folder in base_dir.iterdir():
        if niche_folder.is_dir():
            niche = niche_folder.name
            for file in niche_folder.glob("*.txt"):
                try:
                    print(f"\nProcessing {file.name} in niche: {niche}")
                    generate_video_from_script(str(file), niche)
                except Exception as e:
                    print(f"❌ Failed to create video for {file.name}: {e}")

if __name__ == "__main__":
    run_all_videos()
