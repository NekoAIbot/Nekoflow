from local_script_generator import load_local_model, generate_script
from combine_sources import combine_sources
import os

# Choose 'fast' or 'smart'
mode = "smart"  # Change to "smart" for GPT-Neo 1.3B

# Load trending titles
titles = combine_sources()

# Load model
generator = load_local_model(size=mode)

# Folder to save scripts
os.makedirs("scripts", exist_ok=True)

limit = 3

for i, title in enumerate(titles[:limit], start=1):
    print(f"\n📌 Generating Script {i}: {title}\n")

    prompt = f"""
You are a skilled YouTube scriptwriter known for making viral, engaging videos.

Write a complete, compelling YouTube script based on this trending headline:
"{title}"

🧠 Guidelines:
- Start with a bold hook that grabs attention.
- Provide a short but powerful summary of the headline.
- Use simple, dramatic language that speaks to the average viewer.
- Include emotional and factual angles.
- End with a call to action (like, comment, subscribe).

🎯 Keep the entire script under 250 words.
Begin now:
"""

    script = generate_script(prompt, generator)
    script = script.split("Begin now:")[-1].strip()

    if "subscribe" not in script.lower():
        script += "\n\n💬 Don't forget to like, comment, and subscribe!"

    # Save script
    safe_title = f"script_{i}.txt"
    with open(os.path.join("scripts", safe_title), "w", encoding="utf-8") as f:
        f.write(f"📰 {title}\n\n{script}")

    print(f"✅ Script {i} saved as {safe_title}")
