import os
import asyncio
import edge_tts

# Directories: scripts (text) and audio (for output)
SCRIPTS_DIR = "scripts"
AUDIO_DIR = "audio"

# Ensure the audio output folder exists
os.makedirs(AUDIO_DIR, exist_ok=True)

# TTS parameters: adjust these if you want different voice, rate, or style.
VOICE = "en-US-AriaNeural"    # A natural, humanlike voice
RATE = "+0%"                  # Normal speaking rate
STYLE = "newscast-casual"     # Suitable for tech news narration

async def generate_audio(text, output_file):
    # Create an Edge TTS communicator and generate audio
    communicator = edge_tts.Communicate(text, voice=VOICE, rate=RATE, style=STYLE)
    await communicator.save(output_file)

def narrate_script(script_file):
    # Reads the script file
    with open(script_file, "r", encoding="utf-8") as f:
        return f.read().strip()

def narrate_all_scripts():
    # Ensure there is at least one script file to process.
    if not os.path.isdir(SCRIPTS_DIR) or not os.listdir(SCRIPTS_DIR):
        print("No script files found in the 'scripts' directory.")
        return

    # Process every .txt file in the scripts folder
    for filename in os.listdir(SCRIPTS_DIR):
        if filename.endswith(".txt"):
            script_path = os.path.join(SCRIPTS_DIR, filename)
            audio_filename = filename.replace(".txt", ".mp3")
            audio_path = os.path.join(AUDIO_DIR, audio_filename)
            print(f"🎤 Narrating {filename}...")
            text = narrate_script(script_path)
            asyncio.run(generate_audio(text, audio_path))
            print(f"✅ Saved audio: {audio_path}")

if __name__ == "__main__":
    narrate_all_scripts()
