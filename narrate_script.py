import os
import asyncio
import edge_tts

# Define directories
SCRIPTS_DIR = "scripts"
AUDIO_DIR = "audio"

# Ensure output folder exists
os.makedirs(AUDIO_DIR, exist_ok=True)

# TTS parameters (customize voice, rate, and style as needed)
VOICE = "en-US-AriaNeural"   # A high-quality, natural voice
RATE = "+0%"                 # Normal speaking rate
STYLE = "newscast-casual"    # Suitable for tech news narration

async def generate_audio(text, output_file):
    communicator = edge_tts.Communicate(text, voice=VOICE, rate=RATE, style=STYLE)
    await communicator.save(output_file)

def narrate_script(script_file):
    with open(script_file, "r", encoding="utf-8") as f:
        script_content = f.read().strip()

    # Optional: Remove headline from the first line if present or any extra spacing
    # Here we assume the script text is ready to be narrated.
    return script_content

def narrate_all_scripts():
    # Process every .txt file in the scripts folder
    for filename in os.listdir(SCRIPTS_DIR):
        if filename.endswith(".txt"):
            script_path = os.path.join(SCRIPTS_DIR, filename)
            audio_filename = filename.replace(".txt", ".mp3")
            audio_path = os.path.join(AUDIO_DIR, audio_filename)
            
            print(f"🎤 Narrating {filename}...")

            text = narrate_script(script_path)
            # Run the TTS function asynchronously
            asyncio.run(generate_audio(text, audio_path))
            print(f"✅ Audio saved: {audio_path}")

if __name__ == "__main__":
    narrate_all_scripts()
