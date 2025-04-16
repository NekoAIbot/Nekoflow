# voice_engine.py
import edge_tts
import asyncio

async def generate_voice(text, filename="temp_audio.mp3", niche="general"):
    voice = "en-US-AriaNeural"
    # Default style is informational. Use a more energetic style for tech.
    style = "informational"
    if niche.lower() == "tech":
        style = "narration-professional"
    try:
        # Attempt to use style; if unsupported, fall back.
        communicator = edge_tts.Communicate(text, voice=voice, rate="+5%", style=style)
    except TypeError:
        communicator = edge_tts.Communicate(text, voice=voice, rate="+5%")
    await communicator.save(filename)
